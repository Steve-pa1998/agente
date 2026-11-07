$base = "C:\Users\Steve\Desktop\agente"
$output = @()
$output += "--- ESTRUCTURA ---"
Get-ChildItem -Path $base -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($base.Length + 1)
    $size = [math]::Round($_.Length / 1KB, 1)
    $output += "  $rel ($size KB)"
}
$output += ""
$claves = @("cerebro.py","bus.md","brand.md","motor_init__.py","motor(coordinator.py","agente_publicador.py","agente_contenido.py","agente_engagement.py","agente_planificador.py","agente_navca.py","agente_leads.py","agente_encuestas.py","optimizer_loop.py","config.py")
foreach ($f in $claves) {
    $path = Join-Path $base $f
    if (Test-Path $path) {
        $output += "--- $f ---"
        $lines = (Get-Content $path -Raw) -split "`n"
        $output += "  [$($lines.Count) lineas]"
        $imports = $lines | Where-Object { $_ -match '^\s*(import|from)\s' }
        if ($imports) { $output += "  IMPORTS:"; $imports | ForEach-Object { $output += "    $($_.Trim())" } }
        $classes = $lines | Where-Object { $_ -match '^\s*class\s+\w+' }
        if ($classes) { $output += "  CLASES:"; $classes | ForEach-Object { $output += "    $($_.Trim())" } }
        $funcs = $lines | Where-Object { $_ -match '^\s*def\s+\w+' }
        if ($funcs) { $output += "  FUNCIONES:"; $funcs | ForEach-Object { $output += "    $($_.Trim())" } }
        $output += ""
    }
}
$output += "--- .MD (headings) ---"
Get-ChildItem -Path $base -Recurse -Filter "*.md" | ForEach-Object {
    $rel = $_.FullName.Substring($base.Length + 1)
    $output += "  $rel"
    $lines = (Get-Content $_.FullName -Raw) -split "`n"
    $headings = $lines | Where-Object { $_ -match '^#{1,4}\s' }
    if ($headings) { $headings | ForEach-Object { $output += "    $($_.Trim())" } }
    else { $output += "    (sin headings)" }
    $output += ""
}
$envPath = Join-Path $base ".env"
if (Test-Path $envPath) {
    $output += "--- .env ---"
    Get-Content $envPath | Where-Object { $_ -match "^[^#].*=" } | ForEach-Object { $output += "  " + ($_.Split("=")[0]).Trim() }
}
$final = $output -join "`n"
$final | Out-File "$base\agente_dump.txt" -Encoding UTF8
$final | Set-Clipboard
Write-Host "Listo. Pega con Ctrl+V"
