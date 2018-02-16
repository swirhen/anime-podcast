#!/usr/bin/env ruby

require 'optparse'
require 'uri'
require 'rss/maker'

config = {}
ARGV.options do |o|
  o.on('-t VAL') {|v| config[:target]   = v }
  o.on('-b VAL') {|v| config[:base_uri] = URI.escape(File::dirname(v + '/a') + '/') }
  o.on('-o VAL') {|v| config[:output]   = v }
  o.on('--title VAL') {|v| config[:title]   = v }
  o.parse!
end

time = Time.now.strftime("%a, %d %b %Y %X +0900")

def get_type(f)
  case File::extname(f)
  when '.mp3'
    return 'audio/mpeg'
  when '.m4a'
    return 'audio/x-m4a'
  when '.mp4'
    return 'video/mp4'
  when '.webm'
    return 'video/webm'
  when '.m4v'
    return 'video/x-m4v'
  when '.mov'
    return 'video/quicktime'
  when '.pdf'
    return 'application/pdf'
  when '.zip'
    return 'application/x-compress'
  end
end

rss = RSS::Maker.make("2.0") do |m|
  rss_uri = config[:base_uri] + File::basename(config[:output])
  m.channel.about       = rss_uri
  m.channel.title       = config[:title] || ''
  m.channel.description = rss_uri
  m.channel.link        = rss_uri
  m.channel.pubDate     = Time.parse(time)
  m.items.do_sort       = true

  Dir::glob(config[:target]).each do |f|
    if File.exist?(f) and File::extname(f) != '.xml' and File::extname(f) != '.txt' then
      i = m.items.new_item
      uri = URI.escape(config[:base_uri] + File::basename(f))
      time = File.mtime(f).strftime("%a, %d %b %Y %X +0900")

      i.author           = 'nobody@example.com'
      i.dc_creator       = 'nobody@example.com'
      i.description      = File::basename f
      i.title            = File::basename f
      i.link             = uri
      i.pubDate          = Time.parse(time)
      i.date             = Time.parse(time)
      i.content_encoded  = uri
      i.enclosure.url    = uri
      i.enclosure.length = File::stat(f).size.to_s
      i.enclosure.type   = get_type(f)
      i.guid.content     = uri
    end
  end
end

File.open(config[:output], 'w') do |f|
  f.write rss.to_s
end
