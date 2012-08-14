#!/usr/bin/env python
#By Gao, Huayan.

from galaxy import eggs
import sys, os

def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()
    
def main():
    outfile = sys.argv[1]
    max_rd_len = sys.argv[2]
    avg_ins = sys.argv[3]
    reverse_seq = sys.argv[4]
    asm_flags = sys.argv[5]
    rank = sys.argv[6]
    q1 = sys.argv[7]
    q2 = sys.argv[8]
    f1 = sys.argv[9]
    f2 = sys.argv[10]
    q  = sys.argv[11]
    f  = sys.argv[12]
    p  = sys.argv[13]
    
    try:
        fout = open(sys.argv[1],'w')
    except:
        stop_err("Output file cannot be opened for writing.")
    
    
#    if len(sys.argv) < 4:
#        os.system("cp %s %s" %(infile,outfile))
#        sys.exit()
   
    print max_rd_len 
    tempstr = "max_rd_len= %s \n" %(max_rd_len) 
    fout.writelines(tempstr)

    tempstr = "[LIB] \n"
    fout.writelines(tempstr)

    tempstr = "avg_ins= %s \n" %(avg_ins) 
    fout.writelines(tempstr)

    tempstr = "reverse_seq= %s \n" %(reverse_seq)
    fout.writelines(tempstr)

    tempstr = "asm_flags= %s \n" %(asm_flags) 
    fout.writelines(tempstr)

    tempstr = "rank= %s \n" %(rank) 
    fout.writelines(tempstr)

    if q1 == 'None': 
	q1=''
    else:
        tempstr = "q1 = %s \n" %(q1)
        fout.writelines(tempstr)

    if q2 == 'None': 
	q2=''
    else:
    	tempstr = "q2 = %s \n" %(q2)
    	fout.writelines(tempstr)
    
    if f1 == 'None': 
	f1=''
    else:
    	tempstr = "f1 = %s \n" %(f1)
    	fout.writelines(tempstr)

    if f2 == 'None': 
	f2=''
    else:
    	tempstr = "f2 = %s \n" %(f2)
    	fout.writelines(tempstr)

    if q == 'None': 
	q=''
    else:
    	tempstr = "q = %s \n" %(q)
    	fout.writelines(tempstr)
    
    if f == 'None': 
	f=''
    else:
    	tempstr = "f = %s \n" %(f)
    	fout.writelines(tempstr)

    if p == 'None': 
	p=''
    else:
    	tempstr = "p = %s \n" %(p)
    	fout.writelines(tempstr)



#    cmdline = "cat %s " %(infile)
#    for inp in sys.argv[3:]:
#        cmdline = cmdline + inp + " "
#    cmdline = cmdline + ">" + outfile
#    try:
#        os.system(cmdline)
#    except:
#        stop_err("Error encountered with cat.")
        
    fout.close

if __name__ == "__main__": main()
