from imagepy import IPy
from imagepy import tools
from imagepy.core.manager import ConfigManager

IPy.curapp.SetTitle('海冰影像分析')
ConfigManager.set('tools', 'Ice Analysis')

catlog = ['geotif_plg', '-', 'landedge_plg', '-', 'result_plgs', '-', 'move_plg', '-', 'Ice Software Instructions', 'TestData And Demo']