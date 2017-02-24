# -*- mode: python -*-

block_cipher = None


a = Analysis(['tinycom\\tinycom.py', 'tinycom.spec'],
             pathex=['C:\\Users\\dp\\Downloads\\tinycom\\tinycom\\'],
             binaries=[],
             datas=[ ('tinycom\\tinycom.ui', '.'), ('tinycom\\settings.ui', '.')],
             hiddenimports=['PySide.QtXml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='tinycom',
          debug=False,
          strip=False,
          upx=True,
          console=False,
	  icon='tinycom\\res\\tinycom.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='tinycom')
