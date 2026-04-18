    <!DOCTYPE html>
    <html>

    <head>
        <title>HASIL PENCARIAN</title>
        <?php include 'css.php'; ?>
    </head>

    <body>

        <a href="index.php"> &lt; Home</a>

        <?php
        if (isset($_POST['search'])) {
            set_time_limit(300);

            $author = $_POST['author'];
            $keyword = $_POST['keyword'];
            $limit = $_POST['limit'];
            echo "<h2>Hasil Pencarian</h2>";
            echo "<p>Penulis: <b>$author</b> | Keyword: <b>$keyword</b></p>";

            $cmd_author = escapeshellarg($author);
            $cmd_keyword = escapeshellarg($keyword);
            $cmd_limit = escapeshellarg($limit);

            $python_path = "python"; //pakai ini aja, tapi harus set environment variable dulu

            $script_path = "searchengine.py";
            $command = "$python_path $script_path $cmd_author $cmd_keyword $cmd_limit 2>&1";

            $output = shell_exec($command);

            $data = json_decode($output, true);

            if ($data === null) {
                echo "<p><b>Error</b></p>";
                echo "<pre>$output</pre>";
            } elseif (empty($data)) {
                echo "<p>Data tidak ditemukan. IP DI BLOK LAGI MUNGKIN.</p>";
            } else {
                echo "<table border='1' cellpadding='5' cellspacing='0'>";
                echo "<thead>
                            <tr bgcolor='white'>
                                <th>No</th>
                                <th>Judul Artikel</th>
                                <th>Penulis</th>
                                <th>Nama Jurnal</th>
                                <th>Tanggal Publikasi</th>
                                <th>Sitasi</th>
                                <th>Nilai Similaritas</th>
                                <th>Aksi</th>
                            </tr>
                        </thead>";
                echo "<tbody>";

                $no = 1;
                foreach ($data as $row) {
                    echo "<tr>";
                    echo "<td>" . $no++ . "</td>";
                    echo "<td>" . $row['title']. "</td>";
                    echo "<td>" . $row['author'] . "</td>";
                    echo "<td>" . $row['journal'] . "</td>";
                    echo "<td>" . $row['publication_date'] . "</td>";
                    echo "<td>" . $row['citations'] . "</td>";
                    echo "<td>" . $row['similarity'] . "</td>";
                    echo "<td><a href='" . $row['link'] . "' target='_blank'>Link Artikel Ilmiah</a></td>";
                    echo "</tr>";
                }

                echo "</tbody>";
                echo "</table>";
            }
        } else {
            echo "<p>ISI DULU DATANYA!!!!!</p>";
        }
        ?>

        <br>
    </body>

    </html>