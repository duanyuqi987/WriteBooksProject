$chaptersDir = "d:\ProgramWork\WriteBooksProject\docs\2026-06-26\小说\熵枢纪元：七重跃迁\章节"
$outDir = "d:\ProgramWork\WriteBooksProject\docs\2026-06-26\小说\熵枢纪元：七重跃迁"
$mdOut = Join-Path $outDir "熵枢纪元：七重跃迁.md"
$txtOut = Join-Path $outDir "熵枢纪元：七重跃迁.txt"

$files = Get-ChildItem $chaptersDir -Filter "chapter-*.md" | Sort-Object Name
Write-Host "Found $($files.Count) chapter files"

$sbMd = New-Object System.Text.StringBuilder
$sbTxt = New-Object System.Text.StringBuilder

# MD header
[void]$sbMd.AppendLine("# 熵枢纪元：七重跃迁")
[void]$sbMd.AppendLine("")
[void]$sbMd.AppendLine("作者：段锦佑")
[void]$sbMd.AppendLine("")
[void]$sbMd.AppendLine("---")
[void]$sbMd.AppendLine("")

foreach ($f in $files) {
    $lines = Get-Content $f.FullName -Encoding UTF8
    $skipForTxt = $false
    $chapterName = ""

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]

        # Detect chapter title
        if ($line -match "^(# 第.+章)") {
            $chapterName = $line
        }

        # Detect skip sections for TXT
        if ($line -eq "## 核心故事概括" -or $line -eq "## 本章技法标注") {
            $skipForTxt = $true
        }
        if ($line -match "^## 第.+卷总结" -or $line -eq "## 第一卷总结") {
            $skipForTxt = $true
        }

        # Resume for allowed section headers
        if ($line -match "^## ") {
            if ($line -eq "## 本章唐诗" -or $line -eq "## 正文") {
                $skipForTxt = $false
            }
            elseif ($line -ne "## 核心故事概括" -and $line -ne "## 本章技法标注" -and
                    $line -notmatch "^## 第.+卷总结" -and $line -ne "## 第一卷总结") {
                $skipForTxt = $false
            }
        }

        # Write to MD (all lines)
        [void]$sbMd.AppendLine($line)

        # Write to TXT (skip core summary + technique annotations + volume summary)
        if (-not $skipForTxt) {
            [void]$sbTxt.AppendLine($line)
        }
    }

    # Chapter separator
    [void]$sbMd.AppendLine("")
    [void]$sbMd.AppendLine("---")
    [void]$sbMd.AppendLine("")
    [void]$sbTxt.AppendLine("")
    [void]$sbTxt.AppendLine("")

    Write-Host "  Processed: $chapterName"
}

# Write MD file
[System.IO.File]::WriteAllText($mdOut, $sbMd.ToString(), [System.Text.UTF8Encoding]::new($false))
$mdSize = (Get-Item $mdOut).Length

# Write TXT file
[System.IO.File]::WriteAllText($txtOut, $sbTxt.ToString(), [System.Text.UTF8Encoding]::new($false))
$txtSize = (Get-Item $txtOut).Length

Write-Host ""
Write-Host "=== Merge Complete ==="
Write-Host "MD: $mdOut"
Write-Host "MD Size: $([math]::Round($mdSize/1MB, 2)) MB ($mdSize bytes)"
Write-Host "TXT: $txtOut"
Write-Host "TXT Size: $([math]::Round($txtSize/1MB, 2)) MB ($txtSize bytes)"
Write-Host "Total chapters: $($files.Count)"
