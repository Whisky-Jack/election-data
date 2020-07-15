ENV["PYTHON"] = "/home/bingley/miniconda3/envs/elections/bin/python"
using PyCall
import Pkg
Pkg.build("PyCall")
