BEGIN { skip=0; yaml=0; first=1 }
/^---$/ && first==1 { yaml=1; next }
/^---$/ && yaml==1 { yaml=0; next }
yaml==1 { next }
{ first=0 }
/^## 核心故事概括/ { skip=1; next }
/^## 本章技法标注/ { skip=1; next }
/^## .*卷总结/ { skip=1; next }
/^## 第一卷总结/ { skip=1; next }
/^## 本章唐诗/ { skip=0 }
/^## 题诗/ { skip=0; print "## 本章唐诗"; next }
/^## 正文/ { skip=0 }
/^## / && !/^## 本章唐诗/ && !/^## 题诗/ && !/^## 正文/ && !/^## 核心故事概括/ && !/^## 本章技法标注/ && !/卷总结/ { skip=0 }
!skip { print }
