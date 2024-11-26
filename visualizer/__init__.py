from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from util.check_platform import get_os

font_path = None

if get_os() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rc('font', family=font_name)
elif get_os() == 'macOS':
    font_path = '/Library/Fonts/Supplemental/AppleGothic.ttf'
    rc('font', family='AppleGothic')
    plt.rcParams['axes.unicode_minus'] = False

__all__ = ['font_path']