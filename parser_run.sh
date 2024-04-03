source venv/bin/activate
python spo_parser.py
echo "Subject: This is a test email" | cat - done_letter.txt  | sendmail -f cpu-2-virt@ruslanakmanov.link cpu-2-virt@ruslanakmanov.link
