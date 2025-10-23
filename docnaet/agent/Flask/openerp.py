#!/usr/bin/python
###############################################################################
# Copyright (C) 2001-2024 Micronaet S.r.l. <https://micronaet.com>
# Developer: Nicola Riolini @thebrush
#            https://it.linkedin.com/in/thebrush
#            https://linktr.ee/nicolariolini
###############################################################################
# pip3 install --no-cache-dir --upgrade -r requirements.txt

import os
import subprocess
import configparser
import pdb
import sys

from flask import Flask, request  # send_from_directory render_template

# import sys
# import traceback


# -----------------------------------------------------------------------------
#                                  Class
# -----------------------------------------------------------------------------
class FlaskDocnaet:
    """ Class for keep Flask and Docnaet App together
    """
    # -------------------------------------------------------------------------
    #                              Constructor:
    # -------------------------------------------------------------------------
    def __init__(self, app):
        """ Constructor
        """
        # Save Flask App:
        self.app = app
        self._read_config_file()

    def _read_config_file(self):
        """ Get config file
        """
        if os.name == 'posix':  # Linux mode
            self.linux = True
            config_filename = 'openerp.cfg'
        else:
            self.linux = False
            config_filename = 'openerp.cfg'  # now are the same, consider WIN

        try:
            data_path = r'C:\Micronaet\Docnaet\Flask\Data'
            config_fullname = os.path.join(data_path, config_filename)

            if not os.path.isfile(config_fullname):
                print('Config file not found: generate {}'.format(
                    config_fullname,
                ))
                # Generate a default file:
                config_file = open(config_fullname, 'w')
                config_file.write(
                    '[docnaet]\r\n'
                    '    public: \\\\server\\docnaet\\public\r\n'
                    '    private: \\\\server\\docnaet\\private\r\n'
                    '[labnaet]\r\n'
                    '    public: \\\\server\\docnaet\\public\r\n'
                    '    private: \\\\server\\docnaet\\private\r\n'
                )
                config_file.close()

            # Config file exist here:
            print('Reading config file: {}'.format(config_fullname))
            config = configparser.ConfigParser()
            config.read([config_fullname])

            self.parameters = {
                'docnaet_public': config.get('docnaet', 'public'),
                'docnaet_private': config.get('docnaet', 'private'),
                'labnaet_public': config.get('labnaet', 'public'),
                'labnaet_private': config.get('labnaet', 'private'),
                'running': True,
            }
        except:
            self.parameters = {
                'running': False,
            }
            print('Error reading config file')

    # -------------------------------------------------------------------------
    # Flask Method:
    # -------------------------------------------------------------------------
    def run(self, debug=True):
        """ Start Flask
        """
        self.app.run(debug=debug)

    def get_block_fullname(self, store_folder, filename):
        """ Utility:
            Extract from 12300.pdf block folder 12\12300.pdf
            @return fullname with block folder
        """
        block = 1000
        try:
            document_id = int(filename.split('.')[0])
            block_folder = os.path.join(store_folder, str(document_id // block))
            fullname = os.path.join(block_folder, filename)
            return fullname
        except:
            pass

        # Default reply always (old mode):
        return os.path.join(store_folder, filename)

    def open_document(self, mode):
        """ Open File system document
        """
        fullname = 'NON ANCORA IMPOSTATO'
        error = ''
        try:
            folder_public = self.parameters.get('{}_public'.format(mode))

            filename = request.args.get('filename')
            fullname = self.get_block_fullname(folder_public, filename)

            if not os.path.isfile(fullname):
                error = 'File not found: {}'.format(os.path.basename(fullname))
                print(error)
            else:
                cmd = 'START {}'.format(fullname)
                proc = subprocess.Popen(cmd.split(), shell=True)
        except:
            print('Error opening {}'.format(fullname))
            error = str(sys.exc_info())

        if error:
            return '''
            <html>
                <header>    
                    <script>
                    </script>
                    <title>Empty</title> 
                </header>
                <body>
                Errore: {}
                </body>
            </html>
            '''.format(error)

        return '''
            <html>
                <header>    
                    <script>
                    </script>
                    <title>Empty</title> 
                </header>
                <body onload="window.location.assign(window.history.back());">
                </body>
            </html>
            '''


# -----------------------------------------------------------------------------
#                             Webserver URI:
# -----------------------------------------------------------------------------
app = Flask(__name__)
MyFlaskDocnaet = FlaskDocnaet(app=app)


@app.route('/')
def home():
    """ Hello test page
    """
    running = MyFlaskDocnaet.parameters.get('running')
    return 'Webserver Docnaet Agent ready! {}'.format(
        'RUNNING' if running else 'NOT RUNNING'
    )


@app.route('/docnaet', methods=['GET'])
def docnaet():
    """ Open FS Docnaet
    """
    return MyFlaskDocnaet.open_document(mode='docnaet')


@app.route('/labnaet', methods=['GET'])
def labnaet():
    """ Open FS Labanet
    """
    return MyFlaskDocnaet.open_document(mode='labnaet')


if __name__ == '__main__':
    MyFlaskDocnaet.run()
