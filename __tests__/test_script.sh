for dir in python js reactjs nodejs cli
do
    cd ${dir}
    bash test_script.sh
    cd ..
done