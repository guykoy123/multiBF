# multiBF

# connection port: 4320
# communication protocol:

client: "HELLO"

server:"KA=\<portnumber\>"

client(every five seconds and in TCP: "ALIVE" (if not sent 3 times, connection is closed)

server: "START=\<password\>,STOP=\<password\>,MD5=\<hexstring\>"
  
client: "NOT FOUND"

server: "START=\<password\>,STOP=\<password\>,MD5=\<hexstring\>"

client: "FOUND=\<password\>"
  
server: "STOP"
