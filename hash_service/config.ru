#\ -p 8080
require './hash_service'
$stdout.sync = true
$stderr.sync = true
run Sinatra::Application