<p class="crest-row">
  <img src="assets/uoa.jpg" alt="Εθνικό και Καποδιστριακό Πανεπιστήμιο Αθηνών">
  <img src="assets/dit.jpg" alt="Τμήμα Πληροφορικής και Τηλεπικοινωνιών">
</p>

# Σημειώσεις - Εισαγωγή στον Προγραμματισμό

Οι σημειώσεις του μαθήματος **Εισαγωγή στον Προγραμματισμό** (Κ04) του Τμήματος
Πληροφορικής και Τηλεπικοινωνιών του ΕΚΠΑ, από τον καθηγητή **Παναγιώτη Σταματόπουλο**.
Ξεκινούν από το τι είναι ένας υπολογιστής και ένα πρόγραμμα και καλύπτουν όλη τη γλώσσα C:
δείκτες, δυναμική μνήμη, δομές, λίστες, δέντρα, αρχεία, τον προεπεξεργαστή, και τέλος
αλγορίθμους ταξινόμησης και αναζήτησης.

Διαβάστε τις σημειώσεις εδώ, ανά κεφάλαιο, ή κατεβάστε τις ολόκληρες:

<p class="downloads">
  <a href="downloads/notes.pdf">Όλες οι σημειώσεις (PDF)</a>
  <a href="downloads/notes-md.zip">Όλες οι σημειώσεις (Markdown)</a>
  <a href="https://github.com/progintro/notes">Πηγαίος κώδικας (GitHub)</a>
</p>

## Κεφάλαια

<table class="lab-index">
  <thead>
    <tr>
      <th>#</th>
      <th>Κεφάλαιο</th>
      <th>Θέματα</th>
      <th>PDF</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td><a href="chapters/00-intro/">Εισαγωγή</a></td>
      <td>υπολογιστές, αλγόριθμοι, γλώσσες προγραμματισμού, μεταγλώττιση και σύνδεση, <code>gcc</code></td>
      <td><a href="downloads/00-intro.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>1</td>
      <td><a href="chapters/01-first-programs/">Πρώτα προγράμματα σε C</a></td>
      <td>Hello world, υπολογισμός του π, Ορθόδοξο Πάσχα, μαγικό τετράγωνο, πεζά σε κεφαλαία</td>
      <td><a href="downloads/01-first-programs.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>2</td>
      <td><a href="chapters/02-types-operators/">Μεταβλητές, τύποι, τελεστές και παραστάσεις</a></td>
      <td>τύποι, σταθερές, δηλώσεις, τελεστές, προτεραιότητα, ΜΚΔ / ΕΚΠ</td>
      <td><a href="downloads/02-types-operators.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>3</td>
      <td><a href="chapters/03-control-flow/">Η ροή του ελέγχου</a></td>
      <td><code>if</code>, <code>switch</code>, <code>while</code>, <code>for</code>, <code>break</code> / <code>continue</code>, <code>goto</code></td>
      <td><a href="downloads/03-control-flow.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>4</td>
      <td><a href="chapters/04-functions/">Συναρτήσεις, εμβέλεια και αναδρομή</a></td>
      <td>συναρτήσεις, εμβέλεια και χρόνος ζωής, αναδρομή, δεκαδικοί / δυαδικοί</td>
      <td><a href="downloads/04-functions.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>5</td>
      <td><a href="chapters/05-pointers-arrays/">Δείκτες και πίνακες</a></td>
      <td>διευθύνσεις, δείκτες, ανάγνωση ακεραίων, πίνακες, ιστόγραμμα</td>
      <td><a href="downloads/05-pointers-arrays.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>6</td>
      <td><a href="chapters/06-memory-strings/">Δυναμική μνήμη, συμβολοσειρές και πολυδιάστατοι πίνακες</a></td>
      <td><code>malloc</code> / <code>free</code>, συμβολοσειρές, ορίσματα γραμμής εντολών, δείκτες σε συναρτήσεις</td>
      <td><a href="downloads/06-memory-strings.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>7</td>
      <td><a href="chapters/07-structs/">Απαριθμήσεις, δομές και ενώσεις</a></td>
      <td><code>enum</code>, <code>struct</code>, αυτο-αναφορικές δομές, <code>typedef</code>, <code>union</code>, πεδία bit</td>
      <td><a href="downloads/07-structs.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>8</td>
      <td><a href="chapters/08-lists-trees/">Λίστες και δυαδικά δέντρα</a></td>
      <td>συνδεδεμένες λίστες, ταξινομημένα δυαδικά δέντρα</td>
      <td><a href="downloads/08-lists-trees.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>9</td>
      <td><a href="chapters/09-io/">Είσοδος και έξοδος</a></td>
      <td><code>printf</code> / <code>scanf</code>, ρεύματα, αρχεία, αντιγραφή αρχείων</td>
      <td><a href="downloads/09-io.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>10</td>
      <td><a href="chapters/10-preprocessor/">Ο προεπεξεργαστής της C</a></td>
      <td><code>#include</code>, <code>#define</code>, μακροεντολές, υπό συνθήκη μεταγλώττιση</td>
      <td><a href="downloads/10-preprocessor.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>11</td>
      <td><a href="chapters/11-sorting-searching/">Ταξινόμηση και αναζήτηση</a></td>
      <td>bubblesort, selection / insertion sort, quicksort, heapsort, σειριακή και δυαδική αναζήτηση</td>
      <td><a href="downloads/11-sorting-searching.pdf">PDF</a></td>
    </tr>
    <tr>
      <td>12</td>
      <td><a href="chapters/12-good-practice/">Καλές πρακτικές, συχνά λάθη και βιβλιογραφία</a></td>
      <td>οδηγίες σωστού προγραμματισμού, συχνά λάθη στην C, βιβλιογραφία</td>
      <td><a href="downloads/12-good-practice.pdf">PDF</a></td>
    </tr>
  </tbody>
</table>

## Σχετικά με τις σημειώσεις

Οι σημειώσεις γράφτηκαν αρχικά ως διαφάνειες σε LaTeX («Σημειώσεις Εισαγωγής στον
Προγραμματισμό», Αθήνα 2022). Το πρωτότυπο βρίσκεται στον φάκελο
[`original/`](https://github.com/progintro/notes/tree/main/original). Εδώ το ίδιο υλικό
έχει μεταφερθεί σε Markdown, από το οποίο παράγονται η ιστοσελίδα και τα PDF.

Βρήκατε λάθος; Ανοίξτε ένα [issue](https://github.com/progintro/notes/issues) ή κάντε
ένα pull request στο αντίστοιχο `chapters/*/README.md`.
