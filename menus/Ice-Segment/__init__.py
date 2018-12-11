from imagepy import IPy
from imagepy import tools
from imagepy.core.manager import ConfigManager

IPy.curapp.SetTitle('海冰影像分析')
ConfigManager.set('tools', 'Ice Analysis')

catlog = ['geotif_plg', '-', 'landedge_plg', '-', 'result_plgs', '-', 'move_plg', '-', 'Difference Demo',
'HD Segment Demo', 'Move Detect Demo', '-', 'Modis Test Data', 'Bohai Landedge', 'HD Ice Image', 
'Thunder Sequence', '-', 'Ice Software Instructions']