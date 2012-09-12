Test Dataset for SOAP

ref.fa, totally 100001bp, is extracted from human18 genome chromoson 12.

Two simulated reads files are test_PE1.fa and test_PE2.fa, each of them 
has 71430 simulated reads. The read length is 35 bp. The insert size is 
500, with SD 20. 

We generated the sample output and log files for anyone to check their 
output. They are test.soap.sample, test.single.sample, builder.log.sample
and soap.log.sample.

test.pl is a autorun demon program for SOAPaligner.

Test command lines:

First Step:
     Run 2bwt-builder to build index files:
     <yourpath>/2bwt-builder ref.fa > builder.log
Second Step:
     Run soap to get the alignment result:
     <yourpath>/soap -a test_PE1.fa -b test_PE2.fa -D ref.fa.index -o test.soap -2 test.single -m 400 -x 600 > soap.log


HowTo Use test.pl for SOAPaligner

1. QuickStart
    chmod 755 test.pl
    ./test.pl -test
2. Command Lines:
    -test          run demon program for SOAPaligner
    -path <string> SOAPaligner package installed directroy
    -help          show help document
