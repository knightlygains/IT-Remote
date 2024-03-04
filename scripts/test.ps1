$object = [PSCustomObject]@{
    computer = "Your mom"
    printers = [PSCustomObject]@{
        Printer1 = "Your mom"
        Printer2 = "Your mom2"
    }
}

foreach ($item in $object.printers) {
    Write-Host $item
}
