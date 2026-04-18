<!DOCTYPE html>
<html>

<head>
    <title>PROJECT IIR</title>
    <?php include 'css.php'; ?>
</head>

<body>

    <h1>PENCARIAN DATA ARTIKEL ILMIAH</h1>

    <form method="POST" action="hasil.php">
        <p>
            Input Nama Penulis:<br>
            <input type="text" name="author" required>
        </p>

        <p>
            Input Keyword Artikel:<br>
            <input type="text" name="keyword" required>
        </p>

        <p>
            Jumlah data:<br>
            <input type="number" name="limit" value="5" min="1" max="20">
        </p>

        <input type="submit" name="search" value="Cari Artikel">
    </form>

</body>

</html>