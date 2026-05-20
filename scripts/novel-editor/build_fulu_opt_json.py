# -*- coding: utf-8 -*-
"""构建附录卷弱章充实+桥接JSON"""
import json

Q = chr(34)

mods = []

def p(ch_id, anchor, new_para, desc=""):
    mods.append({"ch_id":ch_id,"type":"insert_paragraph_after","anchor":anchor,"new_text":new_para,"desc":desc})

def a(ch_id, anchor, new_text, desc=""):
    mods.append({"ch_id":ch_id,"type":"insert_after","anchor":anchor,"new_text":new_text,"desc":desc})

# ================================================================
# 弱章充实 (2处)
# ================================================================

# ch9 剑谱三式 (537->700+)
p('ch9',
  '堵住了追兵的路。',
  '萧逸尘教弟子的时候从来不按顺序教。先教叶落——他说' + Q + '先学怎么结束，再学怎么开始' + Q + '。弟子们不理解：剑法不都是从起手式开始的吗？萧逸尘说：' + Q + '你们先学会怎么死，才知道怎么活。叶落不是输——是知道在哪一刻该收。收得好的人，才有资格学叶起。' + Q + '所以弈剑阁的入门第一课不是挥剑——是看一片银杏叶从枝头落到地面的全过程。看一百遍。然后问自己一个问题：' + Q + '它落的时候——是输了，还是完成了？' + Q,
  desc='ch9剑谱三式-教学扩展')

# ch26 弈剑后传 (521->640+)
p('ch26',
  '这不是任务。这是呼吸。',
  '有人问顾小荷：' + Q + '你又不姓萧，为什么要守着弈剑阁？' + Q + '她想了想说：' + Q + '我姓顾。顾家和萧家之间——隔着好几代人。但银杏树不认姓氏。它只认谁给它浇水、谁在树下站过。萧逸尘站过。萧烈站过。萧默站过。现在轮到我站了。不是因为我是谁的后人——是因为树还在这里。树还在，就需要有人站着。' + Q,
  desc='ch26弈剑后传-守阁扩展')

# ================================================================
# 桥接句 (1处)
# ================================================================

a('ch27', '</h2>', '\n    <p>弈剑阁从暗处走到了明处。而庙堂之上——也有人在用自己的方式延续银杏的故事。</p>\n', desc='bridge-ch27')

out_path = 'd:/ProgramWork/WriteBookProject/tmp_fulu_weak_mods.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(mods, f, ensure_ascii=False, indent=2)
print(f'Written {len(mods)} mods: 2 weak + 1 bridge')
