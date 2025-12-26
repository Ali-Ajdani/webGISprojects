<?php
// distance.php

// گرفتن پارامترها از URL
$x1 = isset($_GET['x1']) ? floatval($_GET['x1']) : null;
$y1 = isset($_GET['y1']) ? floatval($_GET['y1']) : null;
$x2 = isset($_GET['x2']) ? floatval($_GET['x2']) : null;
$y2 = isset($_GET['y2']) ? floatval($_GET['y2']) : null;

// تابع محاسبه فاصله بین دو نقطه
function distanceBetweenPoints($x1, $y1, $x2, $y2) {
    $dx = $x2 - $x1;
    $dy = $y2 - $y1;
    return sqrt($dx * $dx + $dy * $dy);
}

header('Content-Type: text/html; charset=utf-8');

echo "<!DOCTYPE html>";
echo "<html lang='fa'>";
echo "<head><meta charset='utf-8'><title>Distance Calculator</title></head>";
echo "<body>";
echo "<h2>محاسبه فاصله بین دو نقطه</h2>";

if ($x1 === null || $y1 === null || $x2 === null || $y2 === null) {
    echo "<p style='color:red;'>لطفاً مختصات را از طریق URL ارسال کنید.</p>";
    echo "<p>فرمت نمونه:</p>";
    echo "<code>?x1=0&y1=0&x2=3&y2=4</code>";
} else {
    $distance = distanceBetweenPoints($x1, $y1, $x2, $y2);

    echo "<p>نقطه اول: (" . htmlspecialchars($x1) . ", " . htmlspecialchars($y1) . ")</p>";
    echo "<p>نقطه دوم: (" . htmlspecialchars($x2) . ", " . htmlspecialchars($y2) . ")</p>";
    echo "<hr>";
    echo "<p><strong>فاصله بین دو نقطه: " . $distance . "</strong></p>";
}

echo "</body></html>";
