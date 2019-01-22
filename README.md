CorrectHighOrders
===========

A plug-in for Nion Swift¹ that calculates the lens excitations for high-order aberrations from the correction matrix.

Installation and Requirements
========================

Requirements
------------
* Python >= 3.6 (lower versions might work but are untested)
* numpy (should be already installed if you have Swift installed)
* scipy (should be already installed if you have Swift installed)

Installation
------------
The recommended way is to use git to clone the repository as this makes receiving updates easy:
```bash
git clone https://github.com/brow71189/CorrectHighOrders
```

If you do not want to use git you can also use github's "download as zip" function and extract the code afterwards.

Once you have the repository on your computer, enter the folder "CorrectHighOrders" and run the following from a terminal:

```bash
python setup.py install
```

It is important to run this command with __exactly__ the python version that you use for running Swift. If you installed Swift according to the online documentation (https://nionswift.readthedocs.io/en/stable/installation.html#installation) you should run `conda activate nionswift` in your terminal before running the above command.

¹ www.nion.com/swift