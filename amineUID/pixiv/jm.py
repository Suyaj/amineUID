import base64

import jmcomic, os, yaml
from jmcomic import ZipPlugin, JmModuleConfig, Img2pdfPlugin, JmPhotoDetail, JmAlbumDetail, jm_log, DirRule

from gsuid_core.logger import logger
from gsuid_core.plugins.amineUID.amineUID.utils.contants import JM_PATH


class ZipEnhancedPlugin(ZipPlugin):
    plugin_key = 'zipEnhancedPlugin'

    def invoke(self, downloader, album: JmAlbumDetail = None, photo: JmPhotoDetail = None, delete_original_file=False,
               level='photo', filename_rule='Ptitle', suffix='zip', zip_dir='./') -> None:
        super().invoke(downloader, album, photo, delete_original_file, level, filename_rule, suffix, zip_dir)
        os.removedirs(os.path.join(zip_dir, album.name))

    def zip_album(self, album, photo_dict: dict, zip_path, path_to_delete):
        """
        压缩album文件夹
        """
        album_dir = self.option.dir_rule.decide_album_root_dir(album)
        import pyzipper
        with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as f:
            f.setpassword('jmPassword'.encode('utf-8'))
            for pdf in os.listdir(album_dir):
                file_path = os.path.join(album_dir, pdf)
                f.write(filename=file_path, arcname=pdf)
                path_to_delete.append(file_path)
        logger.info(f'压缩本子[{album.album_id}]成功 → {zip_path}', 'finish')


class Img2pdfEnhancedPlugin(Img2pdfPlugin):
    plugin_key = 'img2pdfEnhancedPlugin'

    def invoke(self, photo: JmPhotoDetail = None, album: JmAlbumDetail = None, downloader=None, pdf_dir=None,
               filename_rule='Pid', delete_original_file=False, **kwargs):
        if photo is None and album is None:
            jm_log('wrong_usage', 'img2pdf必须运行在after_photo或after_album时')

        try:
            import img2pdf
        except ImportError:
            logger.warning("缺少img2pdf")
            self.warning_lib_not_install('img2pdf')
            return

        self.delete_original_file = delete_original_file

        # 处理生成的pdf文件的路径
        pdf_dir = self.ensure_make_pdf_dir(pdf_dir)

        # 处理pdf文件名
        filename = DirRule.apply_rule_directly(album, photo, filename_rule)

        # pdf路径
        pdf_filepath = os.path.join(pdf_dir, photo.from_album.name, f'{filename}.pdf')

        # 调用 img2pdf 把 photo_dir 下的所有图片转为pdf
        img_path_ls, img_dir_ls = self.write_img_2_pdf(pdf_filepath, album, photo)
        logger.info(f'Convert Successfully: JM{album or photo} → {pdf_filepath}')

        # 执行删除
        img_path_ls += img_dir_ls
        self.execute_deletion(img_path_ls)


def get_album_zip(album_id):
    config = os.path.join(JM_PATH, 'option.yml')
    loadConfig = jmcomic.JmOption.from_file(config)
    with open(config, "r", encoding="utf8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        path = data["dir_rule"]["base_dir"]
        file_path = os.path.join(path, str(album_id) + ".zip")
        if os.path.exists(file_path):
            print("文件：《%s》 已存在，跳过" % album_id)
        else:
            print("开始转换：%s " % album_id)
            album, download = jmcomic.download_album(album_id, loadConfig)
            return album


def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        # 读取文件内容
        file_content = file.read()
        # 将文件内容编码为Base64
        base64_encoded = base64.b64encode(file_content)
        # 将Base64编码转换为字符串
        base64_string = base64_encoded.decode('utf-8')
        return 'base64://' + base64_string


def default_jm_logging(topic: str, msg: str):
    logger.info(f"topic: {topic}, msg: {msg}")

if __name__ == "__main__":
    JmModuleConfig.register_plugin(ZipEnhancedPlugin)
    JmModuleConfig.register_plugin(Img2pdfEnhancedPlugin)
    JmModuleConfig.EXECUTOR_LOG = default_jm_logging
    # 自定义设置：
    album_zip = get_album_zip(544188)
    print("结束")
