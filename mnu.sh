#!/usr/bin/env bash
# �f�B���N�g�����l�[���p�V�F��
# �f�B���N�g����A��+�X�y�[�X���Ƀ��l�[������
# 92�`99�A00�ŊJ�n����f�B���N�g���͖���
# sh���Ė��O��dir������
# ���� "-r" ������Ɛ擪�̘A�ԂƃX�y�[�X���폜
cnt=1
for dir in *
do
    if [[ "${dir}" =~ ^9[2-9]|^00|^sh ]]; then
        echo "${dir} : �������O"
    else
        if [ -d "${dir}" ]; then
            NAME=`echo "${dir}" | sed "s/^[0-9][0-9]\ \(.*\)/\1/"`
            #NUM=`echo "${dir}" | sed "s/^\([0-9][0-9]\)\ .*/\1/"`
            cntd=`printf %02d ${cnt}`

            if [ $# -ne 0 -a "$1" = "-r" -a "${dir}" != "${NAME}" ]; then
                echo "# rename ${dir} -> ${NAME}"
                mv "${dir}" "${NAME}"
            elif [ "${dir}" != "${cntd} ${NAME}" ]; then
                echo "# rename ${dir} -> ${cntd} ${NAME}"
                mv "${dir}" "${cntd} ${NAME}"
            fi
            (( cnt++ ))
        fi
    fi
done
