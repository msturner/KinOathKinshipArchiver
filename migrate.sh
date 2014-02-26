# This script exists only to migrate the svn branches correctly into git. 
# Secondarily this script will also migrate the tickets from track to github, hopefully with all the commit triggers/references intact.
git svn clone https://svn.mpi.nl/LAT --authors-file=users.txt  --branches=IntegrationTests/trunk/Kinoathtestcases.txt --branches=documentation/manuals/kinoath --trunk=Kinnate/trunk --branches=Kinnate/branches

python trac2github.py user@sample.com PeterWithers KinOathKinshipArchiver