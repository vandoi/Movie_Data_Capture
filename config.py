import os
import configparser
import codecs

class Config:
    def __init__(self, path: str = "config.ini"):
        # initialize fields
        self._leftover = []
        self._filter_names = []

        if os.path.exists(path):
            self.conf = configparser.ConfigParser()
            try:
                self.conf.read(path, encoding="utf-8-sig")
            except:
                self.conf.read(path, encoding="utf-8")
        else:
            print("[-] Config file not found! Use the default settings")
            self.conf = self._default_config()

        # parse config that need to be converted to list
        self._parse_to_list()
        self._parse_filter_names()

    def main_mode(self) -> str:
        try:
            return self.conf.getint("common", "main_mode")
        except ValueError:
            self._exit("common:main_mode")

    def failed_folder(self) -> str:
        return self.conf.get("common", "failed_output_folder")

    def success_folder(self) -> str:
        return self.conf.get("common", "success_output_folder")

    def soft_link(self) -> bool:
        return self.conf.getboolean("common", "soft_link")
    def failed_move(self) -> bool:
        return self.conf.getboolean("common", "failed_move")
    def auto_exit(self) -> bool:
        return self.conf.getboolean("common", "auto_exit")
    def transalte_to_sc(self) -> bool:
        return self.conf.getboolean("common", "transalte_to_sc")

    def proxy(self) -> [str, int, int, str]:
        try:
            sec = "proxy"
            proxy = self.conf.get(sec, "proxy")
            timeout = self.conf.getint(sec, "timeout")
            retry = self.conf.getint(sec, "retry")
            proxytype = self.conf.get(sec, "type")
            return proxy, timeout, retry, proxytype
        except ValueError:
            self._exit("common")

    def naming_rule(self) -> str:
        return self.conf.get("Name_Rule", "naming_rule")

    def location_rule(self) -> str:
        return self.conf.get("Name_Rule", "location_rule")

    def add_studio_to_number(self) -> bool:
        return self.conf.getboolean("Name_Rule", "add_studio_to_number")
    
    def max_title_len(self) -> int:
        """
        Maximum title length
        """
        try:
            return self.conf.getint("Name_Rule", "max_title_len")
        except:
            return 50

    def update_check(self) -> bool:
        try:
            return self.conf.getboolean("update", "update_check")
        except ValueError:
            self._exit("update:update_check")

    def sources(self) -> str:
        return self.conf.get("priority", "website")

    def escape_literals(self) -> str:
        return self.conf.get("escape", "literals")

    def escape_folder(self) -> str:
        return self.conf.get("escape", "folders")

    def debug(self) -> bool:
        return self.conf.getboolean("debug_mode", "switch")

    def leftover(self):
        return self._leftover

    def filter_names(self):
        return self._filter_names

    def multi_part_abc(self) -> bool:
        return self.conf.getboolean("common", "multi_part_abc")

    def _parse_filter_names(self):
        filter_name_path = self.conf.get("others", "filter_name_path")
        filter_name_path = os.path.abspath(filter_name_path)
        if os.path.isfile(filter_name_path):
            with open(filter_name_path, 'r') as filter_d:
                for line in filter_d:
                    self._filter_names.append(line.rstrip('\n'))
        
    def _parse_to_list(self):
        leftover_str = self.conf.get("others", "leftover")
        self._leftover = leftover_str.split(",")

    @staticmethod
    def _exit(sec: str) -> None:
        print("[-] Read config error! Please check the {} section in config.ini", sec)
        input("[-] Press ENTER key to exit.")
        exit()

    @staticmethod
    def _default_config() -> configparser.ConfigParser:
        conf = configparser.ConfigParser()

        sec1 = "common"
        conf.add_section(sec1)
        conf.set(sec1, "main_mode", "1")
        conf.set(sec1, "failed_output_folder", "failed")
        conf.set(sec1, "success_output_folder", "JAV_output")
        conf.set(sec1, "soft_link", "0")
        conf.set(sec1, "failed_move", "1")
        conf.set(sec1, "auto_exit", "0")
        conf.set(sec1, "transalte_to_sc", "1")

        sec2 = "proxy"
        conf.add_section(sec2)
        conf.set(sec2, "proxy", "")
        conf.set(sec2, "timeout", "10")
        conf.set(sec2, "retry", "3")
        conf.set(sec2, "type", "socks5")

        sec3 = "Name_Rule"
        conf.add_section(sec3)
        conf.set(sec3, "location_rule", "actor + '/' + number")
        conf.set(sec3, "naming_rule", "number + '-' + title")
        conf.set(sec3, "max_title_len", "50")

        sec4 = "update"
        conf.add_section(sec4)
        conf.set(sec4, "update_check", "1")

        sec5 = "priority"
        conf.add_section(sec5)
        conf.set(sec5, "website", "javbus,javdb,fanza,xcity,mgstage,fc2,avsox,jav321,xcity")

        sec6 = "escape"
        conf.add_section(sec6)
        conf.set(sec6, "literals", "\()/")  # noqa
        conf.set(sec6, "folders", "failed, JAV_output")

        sec7 = "debug_mode"
        conf.add_section(sec7)
        conf.set(sec7, "switch", "0")

        sec8 = "others"
        conf.add_section(sec8)
        conf.set(sec8, "leftover", "gallery", "gallery.zip")

        return conf


if __name__ == "__main__":
    config = Config()
    print(config.main_mode())
    print(config.failed_folder())
    print(config.success_folder())
    print(config.soft_link())
    print(config.failed_move())
    print(config.auto_exit())
    print(config.proxy())
    print(config.naming_rule())
    print(config.location_rule())
    print(config.update_check())
    print(config.sources())
    print(config.escape_literals())
    print(config.escape_folder())
    print(config.debug())
    print(config.leftover())
