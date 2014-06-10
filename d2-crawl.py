"""
  This scrapes the illinois state board of elections website for itemized contributions
  for a particular committee.

  Usage: python d2-crawl.py --commid 14590

  if you want to send the output to a file do

         python d2-crawl.py --commid 14590 > output.txt

  You can look up the committee id by using the committee search utility at
  
  http://www.elections.il.gov/campaigndisclosure/committeesearch.aspx

  When you find the committee you want and click on it the url in the window will be
  something like

  http://www.elections.il.gov/campaigndisclosure/CommitteeDetail.aspx?id=14590

  see the value of 14590 in the url? Put that on the command line
  after --commid as in the example

"""


import urllib2
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--commid', help='commid help', default='23897')

args = parser.parse_args()
commid = args.commid

# calderone 14590
# fppac 23897

debug = False

def text_with_newlines(elem):
    text = ''
    for e in elem.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br /':
            text += '\n'
    return text

def committee_d2_links( committee_id=23897, pg=0):
    comm_url = "http://www.elections.il.gov/campaigndisclosure/CommitteeDetail.aspx?id="
    comm_url += str( committee_id) + "&pageindex=" + str( pg)

    comm_filings = urllib2.urlopen( comm_url)
    d2_links = []
    for line in comm_filings:
        if line.find("D2Quarterly.aspx?id=") > 0 or line.find("D-2") > 0:
            d2_links.append( line.strip())

        if line.find("Records") > 0:
            if debug:
                print "pg: ", pg
                print "url: ", comm_url
                print d2_links
                print line.strip()

            comm_filings.close()
            recs = line.split('>')[1].split('<')[0].split()
            if recs[3] != recs[5]:
                if debug:
                    print recs[3], recs[5]
                d2_links = d2_links[:] + committee_d2_links( committee_id, pg+1)[:]
                return d2_links[:]
            else:
                return d2_links[:]

def d2_bits(d2_links):
    d2_bits=[]
    for link in d2_links:
        if link.find('a href="') > 0:
            d2_bits.append( link.split('a href="')[1].split('">')[0])
    return d2_bits

cco=committee_d2_links( committee_id=commid, pg=0)
filedocids =d2_bits(cco)    

who = []
address = []
amt = []
date = []
for fdid in filedocids:
    url = "http://www.elections.il.gov/CampaignDisclosure/" + fdid 
    soup=BeautifulSoup( urllib2.urlopen( url))
    itemized_link = soup.body.find("a", attrs={'id': "ctl00_ContentPlaceHolder1_btnIndivContribItmzd"})
    
    if itemized_link != None:
        full_itemized_link = "http://www.elections.il.gov/CampaignDisclosure/" + itemized_link.get("href")
        if debug:
            print full_itemized_link
        soup_item=BeautifulSoup( urllib2.urlopen( full_itemized_link.replace(" ", "%20")))
        who += [x.text.strip() for x in soup_item.body.find_all("td", attrs={"class":"tdContributedBy"})]
        
        addTMP = [x for x in soup_item.body.find_all("td", attrs={"class":"tdContribAddress"})]
        addy = []
        for ll in addTMP:
            lines = []
            for e in ll.recursiveChildGenerator():
                lines.append( str(e))
            lines2 = [ x for x in lines if x != '<br/>']
            # make the lines 4 lines of address
            # name, street, add2, townstatezip
            if len( lines2) == 4:
                pass
            elif len( lines2) == 3:
                lines2.append("")
                lines2[3] = lines2[2]
                lines2[2] = ""
            addy.append( "\t".join( lines2[1:]))
        address += addy
        amtdate = [x.text.strip() for x in soup_item.body.find_all("td", attrs={"class":"tdContribAmount"})]
        amt += [ x.split(".")[0][1:].replace(",","") for x in amtdate]
        date += [ x.split(".")[1][2:] for x in amtdate]

if debug:
    print "Start output"        
for i in range( len( who)):
    outstr = "\t".join( [ who[i], address[i], date[i], amt[i]])
    print  outstr.encode('utf8', 'replace')

#<th id="ctl00_ContentPlaceHolder1_Itemized Contributions24"
#style="display:none;"></th><td class="tdContributedBy"
#headers="ctl00_ContentPlaceHolder1_thContributedBy"><span>McAdam
#Landscaping</span></td><td class="tdContribAddress"
#headers="ctl00_ContentPlaceHolder1_thAddress"><span>7313
#Franklin<br/>Forest Park, IL 60130 </span></td><td
#class="tdContribAmount"
#headers="ctl00_ContentPlaceHolder1_thAmount"><span>$250.00<br/>3/18/2001</span></td><td
#class="tdDescription"
#headers="ctl00_ContentPlaceHolder1_thDescription"><span>Individual
#Contribution</span><span></span><a
#href="CommitteeDetail.aspx?id=14590"><br/>Citizens for Anthony
#Calderone</a></td><td class="tdVendorName"
#headers="ctl00_ContentPlaceHolder1_thVendorName"><span></span></td><td
#class="tdVendorAddress"
#headers="ctl00_ContentPlaceHolder1_thVendorAddress"><span></span></td>
