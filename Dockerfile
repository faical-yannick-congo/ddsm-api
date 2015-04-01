FROM ubuntu:14.04

# Update packages
RUN apt-get update -y

# Install Python Setuptools
RUN apt-get install -y python-setuptools

# Install pip
RUN easy_install pip

# Add and install Python modules
ADD requirements.txt /src/requirements.txt
RUN cd /src; pip install -r requirements.txt

# Expose
EXPOSE 5000

# Run
CMD ["python", "/src/run.py", "--host=localhost", "--port=5100"]