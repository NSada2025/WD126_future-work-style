#!/bin/bash
# 認知神経科学ブループリントPDF生成スクリプト

echo "📄 PDF生成を開始します..."

# Pandocがインストールされているか確認
if ! command -v pandoc &> /dev/null; then
    echo "❌ Pandocがインストールされていません"
    echo "以下のコマンドでインストールしてください："
    echo "sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended texlive-lang-japanese"
    exit 1
fi

# 統合Markdownファイルを生成
echo "📝 Markdownファイルを統合中..."
python3 create_cognitive_neuro_pdf.py

# PDFを生成
echo "🔄 PDF変換中..."
pandoc COGNITIVE_NEUROSCIENCE_COMPLETE_BLUEPRINT.md \
    -o cognitive_neuroscience_blueprint.pdf \
    --pdf-engine=xelatex \
    --highlight-style=tango \
    --toc \
    --toc-depth=3 \
    -V documentclass=ltjarticle \
    -V classoption=a4paper \
    -V geometry:margin=25mm \
    -V mainfont="Noto Sans CJK JP"

# HTML版も生成（プレビュー用）
echo "🌐 HTML版も生成中..."
pandoc COGNITIVE_NEUROSCIENCE_COMPLETE_BLUEPRINT.md \
    -o cognitive_neuroscience_blueprint.html \
    --standalone \
    --toc \
    --toc-depth=3 \
    --css=github-markdown.css \
    --highlight-style=github

echo "✅ 生成完了！"
echo "📄 PDF: cognitive_neuroscience_blueprint.pdf"
echo "🌐 HTML: cognitive_neuroscience_blueprint.html"

# プライベートリポジトリ用のディレクトリを作成
echo "📁 プライベートリポジトリ用ディレクトリを準備中..."
mkdir -p private_repo_content/{docs,images,code}
cp cognitive_neuroscience_blueprint.pdf private_repo_content/docs/
cp COGNITIVE_NEUROSCIENCE_COMPLETE_BLUEPRINT.md private_repo_content/docs/
cp -r docs/* private_repo_content/docs/ 2>/dev/null || true

echo "🎉 完了！private_repo_content/に必要なファイルが準備されました"
