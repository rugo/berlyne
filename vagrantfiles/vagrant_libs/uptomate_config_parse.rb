require 'json'

$ports = JSON.parse(File.read(Dir.pwd + "/ports.json"))
$slug = File.basename(File.dirname(Dir.pwd))
