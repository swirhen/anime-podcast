cd "/data/share/temp/voiceactor_nico_ch/08"*
KAI=`cat resent`
../s_crawlnicoch.sh "ウサミン星からう～どっかーん" | grep 第${KAI}回 > archive_dl.sh
if [ -s archive_dl.sh ]; then
  chmod +x archive_dl.sh
  ./archive_dl.sh
  expr ${KAI} + 1 > resent
fi
