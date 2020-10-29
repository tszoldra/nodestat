"""Client to handle connections and actions executed against a remote host."""

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException
from .log import logger
from ast import literal_eval
from psutil._common import bytes2human
import sys

class RemoteClient:
    """Client to interact with a remote host via SSH, SCP and SFTP."""

    def __init__(self, host, user, password, remote_path):
        self.host = host
        self.user = user
        self.password = password
        #self.ssh_key_filepath = ssh_key_filepath
        self.remote_path = remote_path
        self.client = None
        self.scp = None
        self.sftp = None
        self.conn = None

        self.usernames = None
        self.virtual_memory = None
        self.cpu_count_logical = None
        self.cpu_count_physical = None
        self.cpu_freq = None
        self.cpu_times = None
        self.cpu_percent = None
        self.cpu_percent_percpu = None
        self.heavy_processes = []

        # self.__upload_ssh_key()

    # @logger.catch
    # def __get_ssh_key(self):
    #     """ Fetch locally stored SSH key."""
    #     try:
    #         self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
    #         logger.info(f'Found SSH key at self {self.ssh_key_filepath}')
    #     except SSHException as error:
    #         logger.error(error)
    #     return self.ssh_key
    #
    # @logger.catch
    # def __upload_ssh_key(self):
    #     try:
    #         system(f'ssh-copy-id -i {self.ssh_key_filepath}.pub {self.user}@{self.host}>/dev/null 2>&1')
    #         logger.info(f'{self.ssh_key_filepath} uploaded to {self.host}')
    #     except FileNotFoundError as error:
    #         logger.error(error)

    @logger.catch
    def __connect(self):
        """Open connection to remote host. """
        if self.conn is None:
            try:
                self.client = SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(AutoAddPolicy())
                self.client.connect(
                    self.host,
                    username=self.user,
                    password=self.password,
                    #look_for_keys=False,
                    timeout=5000
                )
                self.scp = SCPClient(self.client.get_transport())
                self.sftp = self.client.open_sftp()
            except AuthenticationException as error:
                logger.error(f'Authentication failed {error}')
                sys.exit(-1)
        return self.client

    def disconnect(self):
        """Close SSH & SCP connection."""
        if self.client:
            self.client.close()
        if self.scp:
            self.scp.close()
        if self.sftp:
            self.sftp.close()

    @logger.catch
    def bulk_upload(self, files):
        """
        Upload multiple files to a remote directory.

        :param files: List of local files to be uploaded.
        :type files: List[str]
        """
        self.conn = self.__connect()
        uploads = [self.__upload_single_file(file) for file in files]
        #logger.info(f'Finished uploading {len(uploads)} files to {self.remote_path} on {self.host}')

    def __upload_single_file(self, file):
        """Upload a single file to a remote directory."""
        upload = None
        try:
            self.scp.put(
                file,
                recursive=True,
                remote_path=self.remote_path
            )
            upload = file
        except SCPException as error:
            logger.error(error)
            raise error
        finally:
            #logger.info(f'Uploaded {file} to {self.remote_path}')
            return upload

    def download_file(self, file):
        """Download file from remote host."""
        self.conn = self.__connect()
        self.scp.get(file)

    def remove_file(self, file):
        """Remove file from remote host."""
        self.conn = self.__connect()
        self.sftp.remove(file)

    @logger.catch
    def execute_commands(self, commands):
        """
        Execute multiple commands in succession.

        :param commands: List of unix commands as strings.
        :type commands: List[str]
        """
        self.conn = self.__connect()
        for cmd in commands:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            stdout.channel.recv_exit_status()
            response = stdout.readlines()
            for line in response:
                logger.info(f'INPUT: {cmd} | OUTPUT: {line}')

    @logger.catch
    def check_stats(self):
        self.conn = self.__connect()

        self.bulk_upload(['./nodestat/psutil_script.py'])
        stdin, stdout, stderr = self.client.exec_command("python psutil_script.py")
        stdout.channel.recv_exit_status()
        response = stdout.readlines()

        self.usernames = literal_eval(response[0])
        self.virtual_memory = literal_eval(response[1])
        self.cpu_count_logical = literal_eval(response[2])
        self.cpu_count_physical = literal_eval(response[3])
        self.cpu_freq = literal_eval(response[4])
        self.cpu_times = literal_eval(response[5])
        self.cpu_percent = literal_eval(response[6])
        self.cpu_percent_percpu = literal_eval(response[7])

        self.remove_file("psutil_script.py")

        stdin, stdout, stderr = self.client.exec_command('ps -eo %U,%c,%C --sort=-%cpu --no-headers')
        response = stdout.readlines()
        for line in response:
            splitted_line = line.split(',')
            if float(splitted_line[2]) > 10.0: #cpu usage > 10%
                self.heavy_processes.append([splitted_line[0].strip(), splitted_line[1].strip(), float(splitted_line[2])])

        #logger.info(f'Checked stats for host {self.host}')

    @logger.catch
    def get_stats_row(self, short=False):
        class BColors:  # https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-python
            OKYELLOW = '\x1b[0;30;43m'
            OKGREEN = '\x1b[0;30;42m'
            HIDE = '\x1b[0;30;40m'
            WARNING = '\x1b[0;30;41m'
            ENDC = '\033[0m'

        def colorize_usage_percent(percent):
            if not isinstance(percent, float):
                return percent

            if percent == -1.0: #workaround for tabulate bug with 18 processors
                return BColors.HIDE + str(0.0) + BColors.ENDC
            elif percent > 50:
                return BColors.WARNING + str(percent) + BColors.ENDC
            elif 25 < percent <= 50:
                return BColors.OKYELLOW + str(percent) + BColors.ENDC
            else:
                return BColors.OKGREEN + str(percent) + BColors.ENDC

        def wrap_list(lst, col_width=4, fill=False):
            lst2 = []
            for idx, item in enumerate(lst):
                if idx % col_width == 0:
                    if idx + col_width < len(lst):
                        lst2.append(lst[idx : idx+col_width])
                    else:
                        a = lst[idx: len(lst)]
                        if fill:
                            lst2.append(a + [-1.0] * (col_width - len(a))) #fill the column, workaround for tabulate
                        else:
                            lst2.append(a)
            return lst2

        def list_to_string(lst):
            return " ".join([str(item) for item in lst])

        def list_to_string_2d(lst, color=False, color_only_last_col=False):
            if color and color_only_last_col:
                return "\n".join([list_to_string([item[0], item[1], colorize_usage_percent(item[2])]) for item in lst])
            elif color and (not color_only_last_col):
                return "\n".join([list_to_string([colorize_usage_percent(i) for i in item]) for item in lst])
            else:
                return "\n".join([list_to_string([str(i) for i in item]) for item in lst])

        if short:
            return [self.host,
                    list_to_string_2d(wrap_list(self.usernames, col_width=2)),
                    self.cpu_count_logical,
                    bytes2human(self.virtual_memory.get('total')),
                    bytes2human(self.virtual_memory.get('available')),
                    bytes2human(self.virtual_memory.get('used')),
                    colorize_usage_percent(self.virtual_memory.get('percent')),
                    colorize_usage_percent(self.cpu_percent)
                    ]
        else:
            return [self.host,
                    list_to_string_2d(wrap_list(self.usernames, col_width=2)),
                    self.cpu_count_logical,
                    bytes2human(self.virtual_memory.get('total')),
                    bytes2human(self.virtual_memory.get('available')),
                    bytes2human(self.virtual_memory.get('used')),
                    colorize_usage_percent(self.virtual_memory.get('percent')),
                    colorize_usage_percent(self.cpu_percent),
                    list_to_string_2d(wrap_list(self.cpu_percent_percpu, fill=True), color=True),
                    list_to_string_2d(self.heavy_processes, color=True, color_only_last_col=True)
                    ]


    @logger.catch
    def headers_stats(self, short=False):
        if not short:
            return ['hostname',
                     'users_active',
                     'n_cpu',
                     'mem_tot',
                     'mem_avail',
                     'mem_used',
                     'mem_used [%]',
                     'cpu_load [%]',
                     'cpu_load_per_core [%]',
                     'ps [u, cmd, %cpu > 10%]']
        else:
            return ['hostname',
                     'users_active',
                     'n_cpu',
                     'mem_tot',
                     'mem_avail',
                     'mem_used',
                     'mem_used [%]',
                     'cpu_load [%]']




