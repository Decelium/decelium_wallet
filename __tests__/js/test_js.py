import asyncio
import subprocess
from pyppeteer import launch
import threading
import queue
import psutil,os
# YOU MUST INSTALL CHROME TO USE HEADLESS CHROME
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# dpkg -i google-chrome-stable_current_amd64.deb
# apt-get update
# apt-get install fonts-liberation libasound2 libgbm1 libnspr4 libnss3 libu2f-udev
# apt --fix-broken install -y
# apt-get install -f
# google-chrome-stable --headless --disable-gpu --remote-debugging-port=9222
# which google-chrome-stable
def kill_existing_processes(*process_names):
    """
    Search and terminate processes with the specified names.
    """
    current_pid = os.getpid()  # Get the current process PID
    
    for proc in psutil.process_iter():
        try:
            # Get process details as a named tuple
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            if pinfo['pid'] == current_pid:
                continue            
            # Check if the process name matches or if the cmdline contains the name
            if any(name in pinfo['name'] for name in process_names) or any(name in ' '.join(pinfo['cmdline']) for name in process_names):
                print(f"Killing existing process: {pinfo['name']} with PID: {pinfo['pid']}")
                # Kill the process using SIGKILL (equivalent to kill -9)
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def reader_thread(pipe, q):
    while True:
        line = pipe.readline()
        if line:
            q.put(line)
        else:
            break

async def main():
    flask_process = None
    browser = None
    kill_existing_processes('test_js.py', 'local_flask_server.py', 'chrome')
    try:
        print("starting flask")
        process = subprocess.Popen(
            ['python', 'local_flask_server.py', './'],
            cwd='../../',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Ensures that output is read as string rather than bytes
        )

        # Queues to hold the output
        stdout_q = queue.Queue()
        stderr_q = queue.Queue()

        # Start the reader threads for stdout and stderr
        stdout_thread = threading.Thread(target=reader_thread, args=(process.stdout, stdout_q))
        stderr_thread = threading.Thread(target=reader_thread, args=(process.stderr, stderr_q))

        stdout_thread.start()
        stderr_thread.start()        
        
        # Wait for the server to start
        await asyncio.sleep(5)

        # Check if the process is still running
        print("reading flask")
        retcode = process.poll()
        while not stdout_q.empty():
            print("flask STDOUT:", stdout_q.get().strip())
        while not stderr_q.empty():
            print("flask STDERR:", stderr_q.get().strip())
        
        print("starting browser")
        #browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        browser = await launch(executablePath='/usr/bin/google-chrome-stable',headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

        # Open a new page and navigate to the local Flask server
        print("opening browser page")
        page = await browser.newPage()
        print("navigating browser page")
        await page.goto('http://localhost:5000/decelium_wallet/__tests__/js/index.html')
        print("navigating browser to body")
        await page.waitForSelector('body')

        # Get the body of the root
        print("reading browser content")
        html = await page.content()
        print("reading document.body.textContent")
        text = await page.evaluate('document.body.textContent')
        print("verifying document.body.textContent")
        # Assert some information about the body
        expected_text = 'Hello World!!'
        if expected_text in text:
            print(f'Body contains "{expected_text}"')
        else:
            print(f'Body does not contain "{expected_text}"')

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Close the browser
        # Kill the Flask server subprocess
        try:
            if flask_process:
                print("terminating flask")
                flask_process.terminate()
                print("..waiting flask")
                flask_process.wait()
                print("..closed flask")
            
            if browser:
                print("terminating browser")
                await browser.close()
                print("..closed browser")
        except:
            pass
        finally:
            kill_existing_processes('test_js.py', 'local_flask_server.py', 'chrome')            


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())