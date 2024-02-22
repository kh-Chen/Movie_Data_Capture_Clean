# Movie_Data_Capture_Clean
基于 yoshiko2/Movie_Data_Capture 重写
* 优化代码结构
* 主程序面向过程，依据不同的运行参数拆分模块
* 优化配置文件结构
* 放弃原版中一些奇怪的配置与实现


现有功能：
* `mode_autorate`将指定番号在javdb上标记看过并评分（需要配合javdb.cookies文件）
* `mode_list_movie`输出程序根据配置文件扫描到的影片文件路径以及番号识别结果
* `mode_search`输出指定番号的详细信息
* `mode_test`测试代码或一次性代码
* `mode_url_scraper`将给定的url中包含的影片列表拉取到excel，字段包括
    >"番号","标题","演员","评分","人数","发布日期","磁力","内容","标签"
* `mode_normal`根据配置文件扫描影片，并刮削影片信息，依据配置移动影片文件
  * 下载封面
  * 下载剧照
  * 生成nfo  
* `--specify-file`只刮削指定影片


一些事项：
* 目前虽然移植了avsox, javbus, javdb, msin这四个数据源，但实际上只有javdb进行了实际使用。如果要使用其他数据源，可能导致某些模式下存在问题。比如`mode_url_scraper`模块只实现了javdb
* 移植的数据源刮削器在`core.scrapinglib.custom`下，如需使用其他数据源请自行编写或移植。
* 番号提取器对比原版进行了大幅度简化。如果有什么奇怪的文件名提取番号有问题，可以自己在`utils.number_parser.get_number`中写逻辑分支，或者发出来看看
* 使用的网络库和解析库中经常输出一些错误信息很烦人，所以搞了个`@blockprint`用来屏蔽print。如果你在代码中添加了print但是并没有输出，记得检查添加的代码是否在`@blockprint`影响范围内
* `core.mode_test`是专门用来写测试代码的，使用--test参数运行
* 其他命令行参数详见`config.argsparser`
* 生成nfo文件的逻辑虽然保留了，但是我实际并没有使用过几次，所以很可能现在是不好使的状态。这玩意是真没用。内网环境下smb协议的播放体验薄纱emby和jellyfin之流。海报墙，演员、标签多维度检索等功能看着挺好，实际用起来一言难尽
* 使用整理功能前务必**复制**两个小白鼠影片到单独目录中试运行看看效果。