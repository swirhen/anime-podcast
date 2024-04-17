#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhen.tv auto publish batch
# import section
import datetime
import git
import glob
import math
import os
import pathlib
import re
import sys
import urllib.request
from datetime import datetime as dt
import datetime
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil

# arguments section
SCRIPT_DIR = str(current_dir)
DOWNLOAD_DIR = '/data/share/movie'
OUTPUT_DIR = '/data/share/movie/98 PSP用'
LIST_FILE = f'{SCRIPT_DIR}/checklist.txt'
LIST_TEMP = f'{SCRIPT_DIR}/checklist.temp'
TDATETIME = dt.now()
DATETIME = TDATETIME.strftime('%Y/%m/%d-%H:%M:%S')
DATETIME2 = TDATETIME.strftime('%Y%m%d%H%M%S')
SEED_URI = 'https://nyaa.si/?q=Ohys-Raws&f=0&c=1_4&page=rss'
CHANNEL = 'bot-open'
LOG_DIR = f'{SCRIPT_DIR}/logs'
LOG_FILE = f'{LOG_DIR}/autopub_{DATETIME2}.log'
FLG_FILE = f'{SCRIPT_DIR}/autopub_running'
NEW_PROGRAM_FILE = f'{SCRIPT_DIR}/new_program.txt'
NEW_PROGRAM_FILE_JP = f'{SCRIPT_DIR}/new_program_jp.txt'
LAST_CHECK_DATE_FILE = f'{SCRIPT_DIR}/last_check_date.txt'


# ログ書き込み
def logging(log_str):
    td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
    logstr = f'{td} {log_str}'
    print(logstr)
    swiutil.writefile_append(LOG_FILE, logstr)


# ログ書き込み(時刻無し)
def logging_without_timestamp(log_str):
    print(log_str)
    swiutil.writefile_append(LOG_FILE, log_str)


def multipost(post_str):
    swiutil.multi_post(CHANNEL, post_str)


def multiupload(file_path):
    swiutil.multi_upload(CHANNEL, file_path)


# チェックリストの処理後、git commit -> push(新番組検知があれば新番組ファイルも)
def git_commit_push(new_result_count):
    # 処理の終わったtempリストを降順ソートし、実体に上書き→gitコミット
    with open(LIST_TEMP) as file:
        output_list = sorted(file.readlines(), reverse=True)
    with open(LIST_FILE, 'w') as file:
        file.writelines(output_list)
    repo = git.Repo(SCRIPT_DIR)
    repo.git.commit(LIST_FILE, message='checklist.txt update')
    if new_result_count > 0:
        repo.git.commit(NEW_PROGRAM_FILE, message='new_program.txt update')
        repo.git.commit(NEW_PROGRAM_FILE_JP, message='new_program_jp.txt update')
    repo.git.pull()
    repo.git.push()


# 終了のあとしまつ
def end(proc_date=''):
    os.remove(FLG_FILE)
    # 直近処理時間記録
    if proc_date != '':
        swiutil.writefile_new(LAST_CHECK_DATE_FILE, proc_date)
    exit(0)


# main section
# running flag file check
def main():
    if os.path.isfile(FLG_FILE):
        logging('### running flag file exist.')
        multipost('@here swirhen.tv auto publish: 起動フラグファイルを検知、終了しました\n'
                    '前回異常終了などで残っている場合は削除してください')
        exit(1)
    else:
        flg_file = pathlib.Path(FLG_FILE)
        flg_file.touch()

    logging('### auto publish start.')
    multipost('swirhen.tv auto publish start...')
    # 最終取得時刻
    last_check_date = ''
    with open(LAST_CHECK_DATE_FILE) as file:
        last_check_date = file.read().splitlines()[0]
    # 今回の取得時刻
    nowdt = dt.now()
    now_date = nowdt.strftime('%Y-%m-%d %H:%M')
    # 新番組更新用 5分後時刻
    a5m = nowdt + datetime.timedelta(minutes=5)
    after_five_minute_date = a5m.strftime('%Y-%m-%d %H:%M')

    # DB(5分前に更新)からseedリストを取得
    seed_list = swiutil.get_feed_list(last_check_date)

    # チェックリストの取得
    check_lists = swiutil.make_check_list()

    # リストチェック＆seedダウンロード処理開始：tempリストに日時を出力
    swiutil.writefile_new(LIST_TEMP, f'Last Update: {DATETIME}')

    # 結果リスト
    result = []
    downloads = []
    end_episodes = []
    end_episode_ngs = []

    # チェックリストの行ごとにループ
    for check_list in check_lists:
        last_update = check_list[0]
        episode_number = check_list[1]
        name = check_list[2]
        name_j = check_list[3]
        hit_flag = 0

        seed_episode_number = ''
        # シードリストループ
        for seed_info in seed_list:
            title = seed_info[0]
            link = seed_info[1]
            # titleと一致するかどうかチェック
            if re.search(name, title):
                # 一致した場合、titleから話数の数値を取得
                seed_episode_number = re.sub(r'^.*' + name + r'.* ([0-9.]{2,5}) .*', r'\1', title)
                if not seed_episode_number.replace(".","",1).isdigit():
                    # エピソード番号がとれていない場合、なにかおかしいのでスキップ
                    logging(f'invalid episode number: {seed_episode_number}')
                    continue
                # 新話数 - 旧話数の差分が1のとき、新規エピソードとする
                # 話数には.5などが存在するため、整数で丸めてから計算する(旧話数は切り捨て、新話数は切り上げ)
                episode_number_diff = math.ceil(float(seed_episode_number)) - math.floor(float(episode_number))
                if episode_number_diff == 1:
                    hit_flag = 1
                elif episode_number_diff > 1:
                    # 差分が2以上のときは差分をフラグに入れる
                    hit_flag = episode_number_diff

            if hit_flag > 0:
                logging(f'{title} new episode: {seed_episode_number} local: {episode_number}')
                result.append(title)
                downloads.append([link, title])
                if hit_flag > 1:
                    logging(f'{title}\n    ↑前回との差分が1話以上検出されています。差分話数: {hit_flag}')

                # titleに「END」が含まれるときは終了作品チェックを行う
                if re.search('END', title):
                    filepath = glob.glob(f'{DOWNLOAD_DIR}/*{name_j}')[0]
                    filelist = list(pathlib.Path(filepath).glob(f'{name_j} 第*.mp4'))
                    filelist_ignore_inteval_episodes = sorted([p.name for p in filelist if not re.search(r'\.5|\.1', str(p))])
                    filecount = len(filelist_ignore_inteval_episodes) + 1

                    logging(f'終了とみられるエピソード: {title}')
                    if filecount == int(seed_episode_number):
                        logging(f'    抜けチェック:OK 既存エピソードファイル数(.n話を除く): {str(filecount)} / 最終エピソード番号: {seed_episode_number}')
                        end_episodes.append(name_j)
                    else:
                        logging(f'    抜けチェック:NG 既存エピソードファイル数(.n話を除く): {str(filecount)} / 最終エピソード番号: {seed_episode_number}')
                        end_episode_ngs.append(name_j)

                break

        # 新規エピソードがある場合、最新話数と最終取得日時を更新して、tempリストへ追加
        # 無い場合は元のリストの行をそのまま追加
        if hit_flag > 0:
            swiutil.writefile_append(LIST_TEMP, f'{DATETIME} {seed_episode_number} {name}|{name_j}')
        else:
            swiutil.writefile_append(LIST_TEMP, f'{last_update} {episode_number} {name}|{name_j}')

    # 新番組1話対応
    new_hit_flag = 0
    new_hit_flag_ng = 0
    new_result = []
    new_result_ng = []
    new_links = []
    # シードリストループ
    for seed_info in seed_list:
        title = seed_info[0]
        link = seed_info[1]
        if re.search(' - 01 ', title) and not title in result:
            title_en = re.sub(r'\[.*] (.*) - 01 .*', r'\1', title)
            if re.search('\(', title_en):
                title_en = title_en.split('(')[0]
            # 重複を避けるため、new_program.txtを検索
            if len(swiutil.grep_file(NEW_PROGRAM_FILE, title_en)) == 0:
                new_links.append(link)
                title_ja = swiutil.get_jp_title(title_en)

                if title_ja != '':
                    # 日本語タイトルが取得出来たので重複チェック2：new_program_jp.txt
                    if len(swiutil.grep_file(NEW_PROGRAM_FILE_JP, title_ja)) == 0:
                        # 新番組取得済リストへ追加
                        # チェックリスト(tempと実体両方)に次回取得のためのレコードを追加
                        # 番組名ディレクトリを作成
                        new_hit_flag = 1
                        swiutil.writefile_append(LIST_FILE, f'{DATETIME} 0 {title_en}|{title_ja}')
                        swiutil.writefile_append(LIST_TEMP, f'{DATETIME} 0 {title_en}|{title_ja}')
                        swiutil.writefile_append(NEW_PROGRAM_FILE, title_en)
                        swiutil.writefile_append(NEW_PROGRAM_FILE_JP, title_ja)
                        if not os.path.exists(f'{DOWNLOAD_DIR}/{title_ja}'):
                            os.makedirs(f'{DOWNLOAD_DIR}/{title_ja}')
                        new_result.append(f'{title_ja} ({title_en})')
                else:
                    # 日本語タイトルが取得できなかった1話は何もしないが報告だけする
                    new_hit_flag_ng = 1
                    new_result_ng.append(title_en)

    if new_hit_flag == 1:
        post_msg = '@here 新番組検知！\n' \
                    'リストに追加されたので、次回ダウンロード対象となります\n' \
                    '対象外にする場合は、リストから削除、保存ディレクトリを削除してください\n' \
                    '```' + '\n'.join(new_result) + '```'
        multipost(post_msg)
        logging(post_msg.replace('`',''))

    if new_hit_flag_ng == 1:
        post_msg = '@here 新番組検知！\n' \
                    '検知しましたが、日本語タイトルが検索で取得できなかったので、何もしませんでした\n' \
                    '手動追加を検討してください\n' \
                    '```' + '\n'.join(new_result_ng) + '```'
        multipost(post_msg)
        logging(post_msg.replace('`',''))
    
    # 新番組検知したレコードは次に回すため、取得日時をずらす
    swiutil.update_new_program_feed(new_links, after_five_minute_date)

    # 何らかのエラーで途中で処理が途切れたりして、チェックリスト実体とtempに行数の差が出てしまった場合、警告
    if swiutil.len_file(LIST_FILE) != swiutil.len_file(LIST_TEMP):
        multipost('@channel !!! リスト行数が変化しました。 checklist.txt のコミットログを確認してください')
        logging('!!! リスト行数が変化しました。 checklist.txt のコミットログを確認してください')

    # ここで結果が0ならおわる
    if len(result) == 0:
        git_commit_push(len(new_result))
        post_msg = 'swirhen.tv auto publish completed. (no new episode)'
        multipost(post_msg)
        logging(post_msg)
        end(now_date)

    # seedダウンロード・seed育成処理開始
    dl_links = []
    error_flag = False
    for download in downloads:
        link = download[0]
        title = swiutil.truncate(download[1].translate(str.maketrans('/;!','___')), 247)
        try:
            data = urllib.request.urlopen(link).read()
        except Exception as e:
            logging(f'# download error: {e}')
            error_flag = True
        else:
            with open(f'{DOWNLOAD_DIR}/{title}.torrent', mode='wb') as file:
                file.write(data)
            dl_links.append(link)
    
    if error_flag:
        post_msg = '@channel !!! swirhen.tv auto publish adorted. (seed download error)'
        multipost(post_msg)
        logging(post_msg)
        end()
    else:
        # git commit push
        git_commit_push(len(new_result))
        # DB更新
        swiutil.update_download_feed(dl_links)

    function_log = swiutil.torrent_download(DOWNLOAD_DIR)
    logging_without_timestamp(function_log)

    logging('### movie file rename start.')
    function_log = swiutil.rename_movie_file(DOWNLOAD_DIR)
    logging_without_timestamp(function_log)

    renamed_files = []
    download_files_with_path = sorted(list(pathlib.Path(DOWNLOAD_DIR).glob('*話*.mp4')))
    for dlfwp in download_files_with_path:
        renamed_files.append(dlfwp.name)
    post_msg='renamed movie files:\n' \
                '```' + '\n'.join(renamed_files) + '```'
    multipost(post_msg)
    logging(post_msg.replace('`',''))

    # auto encode
    logging('### auto encode start.')
    function_log = swiutil.encode_movie_in_directory(DOWNLOAD_DIR, OUTPUT_DIR)
    function_log = swiutil.encode_movie_in_directory(DOWNLOAD_DIR, OUTPUT_DIR, 'mkv')
    function_log = swiutil.move_movie(DOWNLOAD_DIR)
    logging_without_timestamp(function_log)

    # 終了エピソードがある場合、終了リストの編集
    # 終了リストがあるかどうかチェック
    resent_end_list_file = sorted(list(pathlib.Path(DOWNLOAD_DIR).glob('end*.txt')))[-1]
    resent_end_list_file_mtime = datetime.date.fromtimestamp(int(os.path.getmtime(resent_end_list_file)))
    now = datetime.date.today()
    if (now - resent_end_list_file_mtime).days >= 30:
        # 30日以上前なので、新しく作る
        year = re.sub(r'end_(....)Q.*', r'\1', resent_end_list_file.name)
        quarter = re.sub(r'.*Q(.).*', r'\1', resent_end_list_file.name)
        if quarter == 4:
            year = int(year) + 1
            quarter = 1
        else:
            quarter = int(quarter) + 1

        resent_end_list_file = pathlib.Path(f'{DOWNLOAD_DIR}/end_{str(year)}Q{str(quarter)}.txt')

    if len(end_episodes) > 0:
        post_msg_end = '# 終了とみられる番組で、抜けチェックOKのため、終了リストに追加/チェックリストから削除\n' \
                        '```' + '\n'.join(end_episodes) + '```'
        multipost(post_msg_end)
        logging(post_msg_end.replace('`',''))
        for end_episode in end_episodes:
            swiutil.sed_del(LIST_FILE, end_episode)
            swiutil.writefile_append(resent_end_list_file, end_episode)

        repo = git.Repo(SCRIPT_DIR)
        repo.git.commit(LIST_FILE, message='checklist.txt update (delete end program)')
        repo.git.pull()
        repo.git.push()

    if len(end_episode_ngs) > 0:
        post_msg_end_ng = '@channel 終了とみられる番組で、抜けチェックNGのため、終了リストにのみ追加(要 抜けチェック)\n' \
                            '```' + '\n'.join(end_episode_ngs) + '```'
        multipost(post_msg_end_ng)
        logging(post_msg_end_ng.replace('`',''))
        for end_episode_ng in end_episode_ngs:
            swiutil.writefile_append(resent_end_list_file, end_episode_ng)

    logging('### all process completed.')
    multipost('swirhen.tv auto publish completed.')
    multiupload(LOG_FILE)

    end(now_date)


if __name__ == '__main__':
    main()
