from bing_image_downloader import downloader
downloader.download("샴고양이", limit=100,  output_dir='dataset', adult_filter_off=True, force_replace=False, timeout=60,resize=(224,224) ,verbose=True)