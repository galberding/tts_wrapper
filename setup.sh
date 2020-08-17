# Use this script to create a new environment, install dependencies and download the used models

ENV_NAME=tttr

function setup_dependencies(){
    # Enter env:
    conda activate $ENV_NAME
    if [ $? == 0 ]; then
        echo "Creating new environment:"
        conda create -n $ENV_NAME python=3.8
        conda activate $ENV_NAME
        if [ $? == 0 ]; then
            echo "Cannot enter conda environment. Is it installed?"
            exit 1
        fi
    fi

    echo "Download models:"
    gdown --id 1dntzjWFg7ufWaTaFy80nRz-Tu02xWZos -O tts_model.pth.tar
    gdown --id 18CQ6G6tBEOfvCHlPqP8EBI4xWbrr9dBc -O config.json
    gdown --id 1Ty5DZdOc0F7OTGj9oJThYbL5iVu_2G0K -O vocoder_model.pth.tar
    gdown --id 1Rd0R_nRCrbjEdpOwq6XwZAktvugiBvmu -O config_vocoder.json
    gdown --id 11oY3Tv0kQtxK_JPgxrfesa99maVXHNxU -O scale_stats.npy

    sudo apt-get install espeak
    pip install -q gdown librosa localimport
    git clone https://github.com/mozilla/TTS
    cd TTS
    git checkout b1935c97
    pip install -r requirements.txt
    python setup.py install
    cd ..
    # Dependencies should be in place
}
