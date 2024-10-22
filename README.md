impositor script i made. takes PDF of single pages, print along short edge (yaw axis)  
like so:  
1      2  |  3      4  

it is suggested to create your PDF in a typesetting program such as Scribus.  

takes file as a PDF and obtains page count automatically.  
every 4 pages is 1 sheet. can input quires, pages, or both, but quires * pages = total page number. then, considering that 4 pages is 1 physical sheet, the original page count should be divisible by 4. number of quires do not have to be even, but number of pages per quire should be even.   

examples of valid parameters:  
PDF page count: 280  
quires: 14  
pages per quire: 20  

PDF page count: 280  
quires: 14  
pages per quire:  

PDF page count: 280  
quires: 
pages per quire: 20  

example of correcting invalid parameters:  
PDF page count: 179  
Page count is not divisible by 4.

PDF page count: 180  
quires:  
pages per quire: 10  
Pages per quire count is not divisble by 4.  
  
PDF page count: 180  
quires: 9  
pages per quire: 20  
