c = get_config()
#c.NotebookApp.password=u'***'
c.NotebookApp.ip = '0.0.0.0'  # to use external IP
c.NotebookApp.open_browser = False
c.NotebookApp.allow_origin = ''
c.NotebookApp.port = 8888
c.NotebookApp.terminado_settings = {'shell_command': ['bash']}
