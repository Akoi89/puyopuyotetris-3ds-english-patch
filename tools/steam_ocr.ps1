# OCR every Steam English texture from the sweep with the Windows built-in engine.
# Output: steam_ocr.json = { "<relative png path>": [ {text, x, y, w, h, words:[{text,x,y,w,h}]} ... ] }
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null = [Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($WinRtTask, $ResultType) { $asTask = $asTaskGeneric.MakeGenericMethod($ResultType); $netTask = $asTask.Invoke($null, @($WinRtTask)); $netTask.Wait(-1) | Out-Null; $netTask.Result }
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$root = 'G:\Claude\PuyoPuyo\work\steam_sweep'
$out = @{}
$files = Get-ChildItem $root -Recurse -Filter '*_en.png'
$i = 0
foreach ($f in $files) {
    $i++
    try {
        $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($f.FullName)) ([Windows.Storage.StorageFile])
        $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        $lines = @()
        foreach ($l in $result.Lines) {
            $words = @()
            $x0 = 1e9; $y0 = 1e9; $x1 = 0; $y1 = 0
            foreach ($w in $l.Words) {
                $r = $w.BoundingRect
                $words += @{ text = $w.Text; x = [int]$r.X; y = [int]$r.Y; w = [int]$r.Width; h = [int]$r.Height }
                if ($r.X -lt $x0) { $x0 = $r.X }; if ($r.Y -lt $y0) { $y0 = $r.Y }
                if (($r.X + $r.Width) -gt $x1) { $x1 = $r.X + $r.Width }; if (($r.Y + $r.Height) -gt $y1) { $y1 = $r.Y + $r.Height }
            }
            $lines += @{ text = $l.Text; x = [int]$x0; y = [int]$y0; w = [int]($x1 - $x0); h = [int]($y1 - $y0); words = $words }
        }
        $rel = $f.FullName.Substring($root.Length + 1).Replace('\', '/')
        $out[$rel] = $lines
        $stream.Dispose()
    } catch {
        Write-Output ("ERR " + $f.FullName + " " + $_.Exception.Message)
    }
    if ($i % 50 -eq 0) { Write-Output ("$i / " + $files.Count) }
}
$json = ConvertTo-Json -InputObject $out -Depth 6 -Compress
[System.IO.File]::WriteAllText('G:\Claude\PuyoPuyo\work\steam_ocr.json', $json, [System.Text.Encoding]::UTF8)
Write-Output ("done " + $out.Count + " textures")
