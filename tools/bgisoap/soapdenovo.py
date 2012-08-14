#!/usr/bin/env python

#import soapdenovo_127mer
import optparse, os, sys, subprocess, tempfile, shutil
from galaxy import eggs
import pkg_resources; pkg_resources.require( "bx-python" )
from bx.cookbook import doc_optparse
#from galaxy import util

def stop_err( msg ):
    sys.stderr.write( '%s\n' % msg )
    sys.exit()

def __main__():
    #Parse Command Line
    parser = optparse.OptionParser()
    parser.add_option( '', '--command_select', dest='command_select', help='Select the kmer version.')
    parser.add_option( '', '--config_file', dest='config_file', help='The input SOAPdenovo configuration file.' )
    parser.add_option( '', '--output_prefix', dest='output_prefix', help='The output file.' )
    ( options, args ) = parser.parse_args()  


    tmp_dir = tempfile.mkdtemp()

#    print command_select
    

    try:
        # exit if input file empty
        if os.path.getsize( options.config_file ) == 0:
            raise Exception, 'Initial file empty'
        # Sort alignments by leftmost coordinates. File <out.prefix>.bam will be created. This command
        # may also create temporary files <out.prefix>.%d.bam when the whole alignment cannot be fitted
        # into memory ( controlled by option -m ).
#        tmp_sorted_aligns_file = tempfile.NamedTemporaryFile( dir=tmp_dir )
#        tmp_sorted_aligns_file_base = tmp_sorted_aligns_file.name
#        tmp_sorted_aligns_file_name = '%s.consesus' % tmp_sorted_aligns_file.name
#        tmp_sorted_aligns_file.close()

#        print command_select

        if options.command_select == "31mer": command0 = "SOAPdenovo_31mer"
        elif options.command_select == "63mer": command0 = "SOAPdenovo_63mer"
        elif options.command_select == "127mer": command0 = "SOAPdenovo_127mer"
        print command0

        command = '%s all -s %s -o %s' % (command0, options.config_file, options.output_prefix )
        print command
        tmp = tempfile.NamedTemporaryFile( dir=tmp_dir ).name
        print tmp
        tmp_stderr = open( tmp, 'wb' )
        proc = subprocess.Popen( args=command, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno() )
        returncode = proc.wait()
        tmp_stderr.close()

        #print os.path.getsize( tmp_sorted_aligns_file_name)

        # get stderr, allowing for case where it's very large
        tmp_stderr = open( tmp, 'rb' )
        stderr = ''
        buffsize = 1048576
        try:
            while True:
                stderr += tmp_stderr.read( buffsize )
                if not stderr or len( stderr ) % buffsize != 0:
                    break
        except OverflowError:
            pass
        tmp_stderr.close()
        if returncode != 0:
            raise Exception, stderr
        # exit if sorted BAM file empty
        if os.path.getsize( options.output_prefix) == 0:
            raise Exception, 'The output file empty'
    except Exception, e:
        #clean up temp files
        if os.path.exists( tmp_dir ):
            shutil.rmtree( tmp_dir )
        stop_err( 'Error in running soapdenovo from (%s), %s' % ( options.config_file, str( e )))


    #clean up temp files
    if os.path.exists( tmp_dir ):
        shutil.rmtree( tmp_dir )
    # check that there are results in the output file
    if os.path.getsize( options.output_prefix ) > 0:
        sys.stdout.write( 'Running End Sucessfully!' )
    else:
        stop_err( 'The output file is empty, there may be an error with your input file.' )

if __name__=="__main__": __main__()
