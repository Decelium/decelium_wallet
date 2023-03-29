for dir in python js reactjs nodejs cli
do
    echo "testing ${dir}"
    cd ${dir}
    bash test_script.sh
    cd ..
done