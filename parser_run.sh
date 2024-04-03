source venv/bin/activate
python spo_parser.py
echo "Subject: This is a test email.\n SPO data collected to DB"  | sendmail -f cpu-2-virt@ruslanakmanov.link cpu-2-virt@ruslanakmanov.link
