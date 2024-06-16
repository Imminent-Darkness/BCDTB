FROM continuumio/miniconda3

WORKDIR /app

# Install git, procps, lsb-release (useful for CLI installs)
RUN apt-get update \
    && apt-get -y install \
            git \
            procps \
            lsb-release \
            ffmpeg \
            libsm6 \
            libxext6 \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
RUN echo "conda activate trading-env" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

# Demonstrate the environment is activated:
RUN echo "Make sure ccxt is installed:"
RUN python -c "import ccxt"

# The code to run when container is started:
COPY . ./
ENTRYPOINT ["./entrypoint.sh"]