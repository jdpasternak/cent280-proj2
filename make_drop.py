"""
Assumes the input file has been created in psql while
logged in as superuser
# create extension pgcrypto;
# \a
# \o functions.txt
# \df
# \o
Then, you enter "functions.txt" for the input file 
and "drop.sql" for the output file.  When asked 
"alter pgcrypto (y/n), respond with 'y'

To create a file that will drop only the functions
owned by 'bob', you can login as bob and do this
=> \a
=> \o myfunctions.txt
=> \df
=> \o
Then, when running this program enter "myfunctions.txt"
for the input file.  Use a name like "drop_myfunctions.sql"
for the output file.  When asked to alter pgcrypto,
respond 'n' for your own functions.  That will allow you 
to drop all the existing functions owned by bob
"""
infilename = input("Enter name of input text file: ")
#infilename = "functions.txt"
infile = open(infilename,"r")
infile.readline()
infile.readline()
lines = infile.readlines()
outfilename = input("Enter name of SQL file to write to: ")
alter_pgcrypto = input("Alter pgcrypto (y/n)? ")
alter_pgcrypto = alter_pgcrypto.strip().lower()
#outfilename = "drop.sql"
outfile = open(outfilename,"w")
for i in range(0, len(lines) - 1):
    tokens = lines[i].strip().split("|")
    func = tokens[1] + '(' + tokens[3] + ');'
    if (func != "digest(text, text);"):
        alter_prefix = "alter extension pgcrypto drop function "
        drop_prefix = "drop function "
        if (alter_pgcrypto == 'y'):
            print(alter_prefix + func)
        print(drop_prefix + func)
        if (alter_pgcrypto == 'y'):
            outfile.write(alter_prefix + func + "\n")
        outfile.write(drop_prefix + func + "\n")
outfile.close()
