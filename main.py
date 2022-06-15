from curses.ascii import isalnum
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import numpy as np
import argparse
import os.path
import pandas as pd
import string
import pyvista as pv
from scipy import interpolate

SIZE_OF_REW_HEADER = 14

coordinateDataPoint = ([])

spl_value_arr= []

class DataPoint:

    def __init__(self, dataFileName):

        self.fileName = dataFileName

        # read text file into pandas DataFrame and create header
        self.df = pd.read_csv(self.fileName, sep=" ", header= SIZE_OF_REW_HEADER, skip_blank_lines=True, names=["Freq", "SPL", "Phase"])

    def get_spl_value_from_freq(self, value):
        result_index = self.df["Freq"].sub(value).abs().idxmin()
        return self.df.at[result_index, "SPL"]
        

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')
# Required positional argument
parser.add_argument('folder_path', type=str,
                    help='A required string positional argument: path of the folder containing data to parse')
# Optional positional argument
parser.add_argument('freq_to_plot', type=int,
                    help='A required int argument: Frequency of the audio spectrum at which we want to plot data')
# Optional positional argument
parser.add_argument('opt_pos_arg', type=int, nargs='?',
                    help='An optional integer positional argument')
# Optional argument
parser.add_argument('--opt_arg', type=int,
                    help='An optional integer argument')
# Switch
parser.add_argument('--switch', action='store_true',
                    help='A boolean switch')
# Parse
args = parser.parse_args()
# Check whether the specified path is an existing directory or is empty
if not os.path.isdir(args.folder_path) or not os.listdir(args.folder_path):
    parser.error("folder_path is not a valid path or is empty")
    # check file format x_y_nameOfFile
if not str(args.freq_to_plot).isnumeric():
    if int(args.freq_to_plot) <= 1 and int(args.freq_to_plot) >= 300 :
     print(str(args.freq_to_plot))
     parser.error("Frequency to plot should be and int value between 1hz and 300hz ")

# Number of measurments is equal to number of files.
nb_measurment_points = len([name for name in os.listdir(args.folder_path) if os.path.isfile(os.path.join(args.folder_path, name))])
# Parse each file and create a DataPoint object 
for name in os.listdir(args.folder_path): 
    if os.path.isfile(os.path.join(args.folder_path, name)):
        #split the string name in three: x coordinate, y coordinate, name of file
        name_split = name.split("_", 2)
        dp = DataPoint(args.folder_path + "/" + str(name))
        #coordinateDataPoint.append([name_split[0], name_split[1], dp])
        spl_value = dp.get_spl_value_from_freq(args.freq_to_plot)
        spl_value_arr.append(spl_value)

print(spl_value_arr)
print(len(spl_value_arr))
zz= np.array(spl_value_arr).reshape(5,5)
print(zz.shape)
print(zz)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# Make data
X = np.arange(0, 5)
Y = np.arange(0, 5)
print(X.shape)
print(X)
X, Y = np.meshgrid(X, Y)
R = np.sqrt(X**2 + Y**2)
Z = np.sin(R)
print(len(Z))
f = interpolate.interp2d(X.squeeze(), Y.squeeze(), zz, kind='cubic')
#f = interpolate.RectBivariateSpline(X,Y,zz)

xnew = np.arange(0, 5, 0.1)
ynew = np.arange(0, 5, 0.1)
znew = f(xnew,ynew)

print(xnew.squeeze().shape)
print(ynew.squeeze().shape)
print(znew.shape)


#xnew = np.arange(-0.1, 2.1, 1e-2)
#ynew = np.arange(-0.1, 2.1, 1e-2)
#znew = f(xnew, ynew)

# Create and plot structured grid
grid = pv.StructuredGrid(xnew.squeeze(), ynew.squeeze(), znew.reshape(2500,0))
#Plot mean curvature as well
grid.plot_curvature(clim=[-1, 1])

# Customize the z axis.
#ax.set_zlim(-1.01, 1.01)
#ax.zaxis.set_major_locator(LinearLocator(10))
## A StrMethodFormatter is used automatically
#ax.zaxis.set_major_formatter('{x:.02f}')
#
## Add a color bar which maps values to colors.
#fig.colorbar(surf, shrink=0.5, aspect=5)
#Plot the surface.
surf = ax.contourf(xnew.squeeze(), ynew.squeeze(), znew, cmap = 'jet', extend='max')
plt.show()