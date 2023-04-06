cd js 
echo "testing js"
python3 test_js.py 
cd ..

cd nodejs 
echo "testing nodejs"
node test_nodejs.js 
cd ..

cd reactjs
echo "testing reactjs"
nodejs test_reactjs.js
cd ..

cd cli
echo "testing cli" 
python3 test_cli.py
cd ..

#cd python
#echo "testing python"
#python3 test_python.py
#cd ..
