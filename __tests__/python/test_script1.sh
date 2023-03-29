rm  .password
rm test_wallet.dec
rm -rf website
mkdir website
cat > website/index.html <<- EOM
<!DOCTYPE html>
<html>
<body>

<p>This text is normal.</p>

<p><em>This text is emphasized.</em></p>

</body>
</html>
EOM
yes | pip uninstall decelium_wallet
pip install "git+https://github.com/Decelium/decelium_wallet.git"
echo "passtest" > .password
python3 test_python.py
result=$?
echo $result
rm .password
rm test_wallet.dec
rm -rf website
if [ $result -eq 0 ]
then
    echo "Python test passes."
    exit 0
else
    echo "Python test fails."
    exit 1
fi


