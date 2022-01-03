#!/usr/bin/bash

[[ -z "$1" ]] && { printf "Usage: $0 <log_file> [<product>]\nExample: $0 log.txt q92"; exit; }

LOGFILE=$1
PATHMAP=s920_map #Set default map file
NUM_SRC_CONTEXT_LINES=3
TOOLCHAIN_PATH="/c/Pax_Prolin_v2.8.16/sdk/toolchains/arm-4.4.1/bin/arm-none-linux-gnueabi-"
ADDR2LINE=$TOOLCHAIN_PATH"addr2line"

[[ -z "$2" ]] || PATHMAP="$2_map" #set map file if it is received as argument

[[ -a "$PATHMAP" ]] || { echo "$PATHMAP not exist" ; exit; } #check if map file exist

old_IFS=$IFS  # save the field separator
IFS=$'\n'     # new field separator, the end of line

for LINE in `grep '#' $LOGFILE`; do
   IFS=$old_IFS     # restore default field separator 
   printf '\n\u001b[31m+----------------------------------------------------------------------------------------------------------------------+\u001b[37m\n'
   
   REMOTE_EXEC=`echo $LINE | cut -d' ' -f2 | cut -d'(' -f1 | sed 's|//|/|'` #parse the module name
   REMOTE_EXEC=`basename $REMOTE_EXEC`
   
   BASE_ADDR=`grep "$REMOTE_EXEC addr" $LOGFILE | cut -d'=' -f2` #parse the base address   

   [[ -z "$BASE_ADDR" ]] && { echo " $REMOTE_EXEC not found" ; continue; }  #next iteration if not found

   echo "Base address=$BASE_ADDR"
      
   LOCAL_EXEC=`grep "$REMOTE_EXEC" $PATHMAP | cut -d'=' -f2`   #search for local module
   echo "Located $REMOTE_EXEC => $LOCAL_EXEC"
      
   ADDR=`echo $LINE | cut -d'[' -f2 | cut -d']' -f1` #search remote absolute address

   printf -v ADDR '%#X' "$((ADDR - BASE_ADDR))"  #calculate local address by subtracting the base address
   #echo "BACKTRACE:  $LOCAL_EXEC $ADDR"
   A2L=`$ADDR2LINE -a $ADDR -e $LOCAL_EXEC -pfC 2>null`  #call binultil address2line to acquire the line information
   #echo "A2L:        $A2L"
   
   FUNCTION=`echo $A2L | sed 's/\<at\>.*//' | cut -d' ' -f2-99` #parse funcion name
   FILE_AND_LINE=`echo $A2L | sed 's/.* at //' | tr '\\\\' '/'` #parse file name and line number
   echo "FILE:       $FILE_AND_LINE"
   echo "FUNCTION:   $FUNCTION"
   
   printf '\u001b[32m\n' #Change text color to green

   # print offending source code
   SRCFILE=`echo $FILE_AND_LINE | cut -d':' -f1`
   SRCFILE+=':'`echo $FILE_AND_LINE | cut -d':' -f2`
   LINENUM=`echo $FILE_AND_LINE | cut -d':' -f3`
   if ([ -f $SRCFILE ]); then
      cat -n $SRCFILE | grep -C $NUM_SRC_CONTEXT_LINES "^ *$LINENUM\>" | sed "s/ $LINENUM/*$LINENUM/"
   else
      echo "File not found: $SRCFILE"
   fi
   IFS=$'\n'     # new field separator, the end of line           
done

IFS=$old_IFS     # restore default field separator 
