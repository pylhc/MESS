ccccc Author : S. Fartoukh
ccccc Version: March 2012 (adding a5/b5/a6 correction)

               program corr_tripD1
	       
	      implicit none
	      integer Na3,Na4,Na5,Na6,Nb3,Nb4,Nb5,Nb6,Nsmax,Nmag
	      integer i,j,k,itot,imag,ic,is
	      parameter(Na3=4,Na4=2,Na5=6,Na6=3,Nb3=6,Nb4=3,Nb5=6,Nb6=4)
	      parameter(Nsmax=100,Nmag=6)
	      integer Nsmag(8,Nmag),Nsmag0(8,Nmag)
	      integer bv,ic0
	       
	       real*8 a2c(8),a2b(8),a2aux(8,Nmag,Nsmax)
	       real*8 a3c(Na3,8),a3b(Na3,8),a3aux(Na3,8,Nmag,Nsmax)
	       real*8 a4c(Na4,8),a4b(Na4,8),a4aux(Na4,8,Nmag,Nsmax)
	       real*8 a5c(Na5,8),a5b(Na5,8),a5aux(Na5,8,Nmag,Nsmax)
	       real*8 a6c(Na5,8),a6b(Na5,8),a6aux(Na6,8,Nmag,Nsmax)
	       real*8 b3c(Nb3,8),b3b(Nb3,8),b3aux(Nb3,8,Nmag,Nsmax)
	       real*8 b4c(Nb4,8),b4b(Nb4,8),b4aux(Nb4,8,Nmag,Nsmax)
	       real*8 b5c(Nb5,8),b5b(Nb5,8),b5aux(Nb5,8,Nmag,Nsmax)
	       real*8 b6c(Nb6,8),b6b(Nb6,8),b6aux(Nb6,8,Nmag,Nsmax)
	       real*8 res(0:6,0:6),akl(2,11)
	       real*8 betx,bety,x,y,racx,racy
	       real*8 scale,scaleD1,scaleD2,scaleMQX
	       real*8 a2cor(8),a3cor(8),a4cor(8),a5cor(8),a6cor(8)
	       real*8 b3cor(8),b4cor(8),b5cor(8),b6cor(8)
	       character*20 charaux
	       real*8 det,aux1,aux2,anorm
	       integer icheck
	       
	       scaleMQX=1
	       scaleD1=1
	       scaleD2=0
	       
	       do i=1,8
	       do imag=1,Nmag
	       Nsmag(i,imag)=0
	       enddo
	       enddo
	       
	       do i=1,8
	       a2cor(i)=0.d0
	       a3cor(i)=0.d0
	       a4cor(i)=0.d0
	       a5cor(i)=0.d0
	       a6cor(i)=0.d0
	       b3cor(i)=0.d0
	       b4cor(i)=0.d0
	       b5cor(i)=0.d0
	       b6cor(i)=0.d0
	       enddo
	             
	       do i=1,8
	       a2c(i)=0.d0
	       a2b(i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       a2aux(i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       	       
	       do j=1,Na3
	       do i=1,8
	       a3c(j,i)=0.d0
	       a3b(j,i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       a3aux(j,i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       enddo
	       	       
	       do j=1,Na4
	       do i=1,8
	       a4c(j,i)=0.d0
	       a4b(j,i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       a4aux(j,i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       enddo
	       
	       do j=1,Na5
	       do i=1,8
	       a5c(j,i)=0.d0
	       a5b(j,i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       a5aux(j,i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       enddo
	       
	       do j=1,Na6
	       do i=1,8
	       a6c(j,i)=0.d0
	       a6b(j,i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       a6aux(j,i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       enddo
	       
	       do j=1,Nb3
	       do i=1,8
	       b3c(j,i)=0.d0
	       b3b(j,i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       b3aux(j,i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       enddo
	       
	       do j=1,Nb4
	       do i=1,8
	       b4c(j,i)=0.d0
	       b4b(j,i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       b4aux(j,i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       enddo
	       
	       do j=1,Nb5
	       do i=1,8
	       b5c(j,i)=0.d0
	       b5b(j,i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       b5aux(j,i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       enddo
	       
	       do j=1,Nb6
	       do i=1,8
	       b6c(j,i)=0.d0
	       b6b(j,i)=0.d0
	       do imag=1,Nmag
	       do is=1,Nsmax
	       b6aux(j,i,imag,is)=0.d0
	       enddo
	       enddo
	       enddo
	       enddo
	       
	       bv=0
	       ic0=0
	       itot=0
	       open(1,file='temp/optics0_inser.mad')
	       
	       do while(.true.)
	       read(1,*,err=99,end=100) charaux,betx,bety,x,y
	       racx=sqrt(betx)
	       racy=sqrt(bety)
	       do i=0,6
	       do j=0,6
	       res(i,j)=racx**i*racy**j
	       enddo
	       enddo
	       
	       if(INDEX(charaux,"L1").ne.0) then
	       ic=1
	       elseif(INDEX(charaux,"R1").ne.0) then
	       ic=2
	       elseif(INDEX(charaux,"L2").ne.0) then
	       ic=3
	       elseif(INDEX(charaux,"R2").ne.0) then
	       ic=4
	       elseif(INDEX(charaux,"L5").ne.0) then
	       ic=5
	       elseif(INDEX(charaux,"R5").ne.0) then
	       ic=6
	       elseif(INDEX(charaux,"L8").ne.0) then
	       ic=7
	       elseif(INDEX(charaux,"R8").ne.0) then
	       ic=8
	       endif
	       
	       if(ic0.eq.0) ic0=ic	       
	       if(ic.eq.ic0+1) then
	       bv=bv+1
	       elseif(ic.eq.ic0-1) then
	       bv=bv-1
	       endif
	       ic0=ic	       	       
	       
	       if(INDEX(charaux,"MQSX").ne.0) then
	       itot=itot+1
	       a2c(ic)=res(1,1)
	       elseif(INDEX(charaux,"MCSX").ne.0) then
	       itot=itot+1
	       b3c(1,ic)=res(3,0)
	       b3c(2,ic)=res(0,3)
	       b3c(3,ic)=res(1,2)
	       b3c(4,ic)=res(2,1)
	       b3c(5,ic)=res(1,1)*y
	       b3c(6,ic)=0.
	       elseif(INDEX(charaux,"MCTX").ne.0) then
	       itot=itot+1
	       b6c(1,ic)=res(6,0)
	       b6c(2,ic)=res(0,6)
	       b6c(3,ic)=res(4,2)
	       b6c(4,ic)=res(2,4)
	       elseif(INDEX(charaux,"MCOSX").ne.0) then
	       itot=itot+1
	       a4c(1,ic)=res(1,3)
	       a4c(2,ic)=res(3,1)
	       elseif(INDEX(charaux,"MCOX").ne.0) then
	       itot=itot+1
	       b4c(1,ic)=res(4,0)
	       b4c(2,ic)=res(0,4)
	       b4c(3,ic)=res(2,2)
	       elseif(INDEX(charaux,"MCSSX").ne.0) then
	       itot=itot+1
	       a3c(1,ic)=res(2,1)
	       a3c(2,ic)=res(1,2)
	       a3c(3,ic)=res(0,3)
	       a3c(4,ic)=res(3,0)
	       elseif(INDEX(charaux,"MCDX").ne.0) then
	       itot=itot+1
	       a5c(1,ic)=res(4,1)
	       a5c(2,ic)=res(1,4)
	       a5c(3,ic)=res(2,3)
	       a5c(4,ic)=res(3,2)
	       a5c(5,ic)=res(0,5)
	       a5c(6,ic)=res(5,0)
	       elseif(INDEX(charaux,"MCDSX").ne.0) then
	       itot=itot+1
	       b5c(1,ic)=res(5,0)
	       b5c(2,ic)=res(0,5)
	       b5c(3,ic)=res(3,2)
	       b5c(4,ic)=res(2,3)
	       b5c(5,ic)=res(1,4)
	       b5c(6,ic)=res(4,1)
	       elseif(INDEX(charaux,"MCTSX").ne.0) then
	       itot=itot+1
	       a6c(1,ic)=res(5,1)
	       a6c(2,ic)=res(1,5)
	       a6c(3,ic)=res(3,3)
	       else
	       if(INDEX(charaux,"MQX").ne.0) then
	        if(INDEX(charaux,"MQXA.1").ne.0.or.
     +             INDEX(charaux,"MQXC.1").ne.0) then
	        itot=itot+1
	        imag=1
		scale=scaleMQX
	        elseif(INDEX(charaux,"MQXB.A").ne.0.or.
     +                 INDEX(charaux,"MQXD.A").ne.0) then
	        itot=itot+1
	        imag=2
	        scale=scaleMQX
	        elseif(INDEX(charaux,"MQXB.B").ne.0.or.
     +                 INDEX(charaux,"MQXD.B").ne.0) then
	        itot=itot+1
	        imag=3
	        scale=scaleMQX
	        elseif(INDEX(charaux,"MQXA.3").ne.0.or.
     +                 INDEX(charaux,"MQXC.3").ne.0) then
	        itot=itot+1
	        imag=4
	        scale=scaleMQX
	        endif
	        elseif(INDEX(charaux,"MBX").ne.0) then
	        itot=itot+1
	        imag=5
	        scale=scaleD1
	        elseif(INDEX(charaux,"MBRC.").ne.0.or.
     +                 INDEX(charaux,"MBRD.").ne.0) then
	        itot=itot+1
	        imag=6
	        scale=scaleD2
	        endif
		
		Nsmag(ic,imag)=Nsmag(ic,imag)+1
		is=Nsmag(ic,imag)
		
		if(is.gt.Nsmax) then
	        write(6,*) 'Too many slices in element', charaux
	        stop
	        endif
	       
	       a2aux(ic,imag,is)  =res(1,1)*scale
	       a3aux(1,ic,imag,is)=res(2,1)*scale
	       a3aux(2,ic,imag,is)=res(1,2)*scale
	       a3aux(3,ic,imag,is)=res(0,3)*scale
	       a3aux(4,ic,imag,is)=res(3,0)*scale
	       a4aux(1,ic,imag,is)=res(1,3)*scale
	       a4aux(2,ic,imag,is)=res(3,1)*scale
	       a5aux(1,ic,imag,is)=res(4,1)*scale
	       a5aux(2,ic,imag,is)=res(1,4)*scale
	       a5aux(3,ic,imag,is)=res(2,3)*scale
	       a5aux(4,ic,imag,is)=res(3,2)*scale
	       a5aux(5,ic,imag,is)=res(0,5)*scale
	       a5aux(6,ic,imag,is)=res(5,0)*scale
	       a6aux(1,ic,imag,is)=res(5,1)*scale
	       a6aux(2,ic,imag,is)=res(1,5)*scale
	       a6aux(3,ic,imag,is)=res(3,3)*scale
	       b3aux(1,ic,imag,is)=res(3,0)*scale
	       b3aux(2,ic,imag,is)=res(0,3)*scale
	       b3aux(3,ic,imag,is)=res(1,2)*scale
	       b3aux(4,ic,imag,is)=res(2,1)*scale
	       b3aux(5,ic,imag,is)=res(1,1)*y*scale
	       b3aux(6,ic,imag,is)=0.*scale
	       b4aux(1,ic,imag,is)=res(4,0)*scale
	       b4aux(2,ic,imag,is)=res(0,4)*scale
	       b4aux(3,ic,imag,is)=res(2,2)*scale
	       b5aux(1,ic,imag,is)=res(5,0)*scale
	       b5aux(2,ic,imag,is)=res(0,5)*scale
	       b5aux(3,ic,imag,is)=res(3,2)*scale
	       b5aux(4,ic,imag,is)=res(2,3)*scale
	       b5aux(5,ic,imag,is)=res(1,4)*scale
	       b5aux(6,ic,imag,is)=res(4,1)*scale
	       b6aux(1,ic,imag,is)=res(6,0)*scale
	       b6aux(2,ic,imag,is)=res(0,6)*scale
	       b6aux(3,ic,imag,is)=res(4,2)*scale
	       b6aux(4,ic,imag,is)=res(2,4)*scale
	       
	       endif
	       
  99           continue
  
               enddo
	       
 100           continue
               
	       write(6,*) '***************IR1***************'
               write(6,'(i3,1x,a30)') Nsmag(1,1),'slices for Q1.L1' 
               write(6,'(i3,1x,a30)') Nsmag(2,1),'slices for Q1.R1' 
               write(6,'(i3,1x,a30)') Nsmag(1,2),'slices for Q2a.L1' 
               write(6,'(i3,1x,a30)') Nsmag(2,2),'slices for Q2a.R1' 
               write(6,'(i3,1x,a30)') Nsmag(1,3),'slices for Q2b.L1' 
               write(6,'(i3,1x,a30)') Nsmag(2,3),'slices for Q2b.R1' 
               write(6,'(i3,1x,a30)') Nsmag(1,4),'slices for Q3.L1' 
               write(6,'(i3,1x,a30)') Nsmag(2,4),'slices for Q3.R1' 
               write(6,'(i3,1x,a30)') Nsmag(1,5),'slices for D1.L1' 
               write(6,'(i3,1x,a30)') Nsmag(2,5),'slices for D1.R1' 
               write(6,*) '***************IR5***************'
               write(6,'(i3,1x,a30)') Nsmag(5,1),'slices for Q1.L5' 
               write(6,'(i3,1x,a30)') Nsmag(6,1),'slices for Q1.R5' 
               write(6,'(i3,1x,a30)') Nsmag(5,2),'slices for Q2a.L5' 
               write(6,'(i3,1x,a30)') Nsmag(6,2),'slices for Q2a.R5' 
               write(6,'(i3,1x,a30)') Nsmag(5,3),'slices for Q2b.L5' 
               write(6,'(i3,1x,a30)') Nsmag(6,3),'slices for Q2b.R5' 
               write(6,'(i3,1x,a30)') Nsmag(5,4),'slices for Q3.L5' 
               write(6,'(i3,1x,a30)') Nsmag(6,4),'slices for Q3.R5' 
               write(6,'(i3,1x,a30)') Nsmag(5,5),'slices for D1.L5' 
               write(6,'(i3,1x,a30)') Nsmag(6,5),'slices for D1.R5' 
               write(6,*) '***************IR2***************'
               write(6,'(i3,1x,a30)') Nsmag(3,1),'slices for Q1.L2' 
               write(6,'(i3,1x,a30)') Nsmag(4,1),'slices for Q1.R2' 
               write(6,'(i3,1x,a30)') Nsmag(3,2),'slices for Q2a.L2' 
               write(6,'(i3,1x,a30)') Nsmag(4,2),'slices for Q2a.R2' 
               write(6,'(i3,1x,a30)') Nsmag(3,3),'slices for Q2b.L2' 
               write(6,'(i3,1x,a30)') Nsmag(4,3),'slices for Q2b.R2' 
               write(6,'(i3,1x,a30)') Nsmag(3,4),'slices for Q3.L2' 
               write(6,'(i3,1x,a30)') Nsmag(4,4),'slices for Q3.R2' 
               write(6,'(i3,1x,a30)') Nsmag(3,5),'slices for D1.L2' 
               write(6,'(i3,1x,a30)') Nsmag(4,5),'slices for D1.R2' 
               write(6,*) '***************IR8***************'
               write(6,'(i3,1x,a30)') Nsmag(7,1),'slices for Q1.L8' 
               write(6,'(i3,1x,a30)') Nsmag(8,1),'slices for Q1.R8' 
               write(6,'(i3,1x,a30)') Nsmag(7,2),'slices for Q2a.L8' 
               write(6,'(i3,1x,a30)') Nsmag(8,2),'slices for Q2a.R8' 
               write(6,'(i3,1x,a30)') Nsmag(7,3),'slices for Q2b.L8' 
               write(6,'(i3,1x,a30)') Nsmag(8,3),'slices for Q2b.R8' 
               write(6,'(i3,1x,a30)') Nsmag(7,4),'slices for Q3.L8' 
               write(6,'(i3,1x,a30)') Nsmag(8,4),'slices for Q3.R8' 
               write(6,'(i3,1x,a30)') Nsmag(7,5),'slices for D1.L8' 
               write(6,'(i3,1x,a30)') Nsmag(8,5),'slices for D1.R8'
	       write(6,*) 
 
c              do imag=1,6
c	       do ic=1,8
c	       write(6,*) imag,ic,Nsmag(ic,imag)
c	       enddo
c	       enddo

               if(bv.gt.0) then
	       bv=1
	       else
	       bv=-1
	       endif
	       write(6,*) 'BEAM DIRECTION',bv
	       write(6,*) 
 
               if(itot.ne.636) then
	write(6,*) "Tot. number of entries in optics0_inser.mad: ", itot
	write(6,*) "Something possibly wrong in file optics0_inser.mad"
	write(6,*)        
	       endif
 
               do ic=1,8,2
	       b3c(6,ic)=b3c(5,ic+1)
	       b3c(6,ic+1)=b3c(5,ic)	       
	       do imag=1,6
	       do is=1,Nsmag(ic,imag)
	       b3aux(6,ic,imag,is)=b3aux(5,ic+1,imag,Nsmag(ic,imag)-is+1)
	       b3aux(6,ic+1,imag,is)=b3aux(5,ic,imag,Nsmag(ic,imag)-is+1)
	       enddo
	       enddo
	       enddo
	       
	      
	      open(1,file='temp/tripD1D2.errors')
	      itot=0
	      
	       do i=1,8
	       do imag=1,Nmag
	       Nsmag0(i,imag)=Nsmag(i,imag)
	       Nsmag(i,imag)=0
	       enddo
	       enddo
	      
	      
	       do while(.true.)
	       read(1,*,err=199,end=200)
     +         charaux,(akl(1,i),akl(2,i),i=1,11)
               
	       if(INDEX(charaux,"L1").ne.0) then
	       ic=1
	       elseif(INDEX(charaux,"R1").ne.0) then
	       ic=2
	       elseif(INDEX(charaux,"L2").ne.0) then
	       ic=3
	       elseif(INDEX(charaux,"R2").ne.0) then
	       ic=4
	       elseif(INDEX(charaux,"L5").ne.0) then
	       ic=5
	       elseif(INDEX(charaux,"R5").ne.0) then
	       ic=6
	       elseif(INDEX(charaux,"L8").ne.0) then
	       ic=7
	       elseif(INDEX(charaux,"R8").ne.0) then
	       ic=8
	       else
	       write(6,*) 'Problem in tripD1D2.errors'
	       write(6,*) 'IR unknown :', charaux
	       stop
	       endif
	       
	       
	       if(INDEX(charaux,"MQX").ne.0) then
	        if(INDEX(charaux,"MQXA.1").ne.0.or.
     +             INDEX(charaux,"MQXC.1").ne.0) then
	        itot=itot+1
	        imag=1
	        elseif(INDEX(charaux,"MQXB.A").ne.0.or.
     +                 INDEX(charaux,"MQXD.A").ne.0) then
	        itot=itot+1
	        imag=2
	        elseif(INDEX(charaux,"MQXB.B").ne.0.or.
     +                 INDEX(charaux,"MQXD.B").ne.0) then
	        itot=itot+1
	        imag=3
	        elseif(INDEX(charaux,"MQXA.3").ne.0.or.
     +                 INDEX(charaux,"MQXC.3").ne.0) then
	        itot=itot+1
	        imag=4
	        endif
	       elseif(INDEX(charaux,"MBX").ne.0) then
	        itot=itot+1
	        imag=5
	       elseif(INDEX(charaux,"MBRC.").ne.0.or.
     +                INDEX(charaux,"MBRD.").ne.0) then
	        itot=itot+1
	        imag=6
	       else
	      write(6,*) 'Magnet unknown :', charaux
	      write(6,*) 'Problem in tripD1D2.errors'
	       stop
	       endif
	       
	       
	       
	       Nsmag(ic,imag)=Nsmag(ic,imag)+1
	       is=Nsmag(ic,imag)
	       
	       if(is.gt.Nsmax) then
	       write(6,*) 'Too many slices in element', charaux
	       stop
	       endif
	       
	       a2b(ic)=a2b(ic)+a2aux(ic,imag,is)*akl(2,2)
	       do i=1,Na3
	       a3b(i,ic)=a3b(i,ic)+a3aux(i,ic,imag,is)*akl(2,3)
	       enddo
	       do i=1,Na4
	       a4b(i,ic)=a4b(i,ic)+a4aux(i,ic,imag,is)*akl(2,4)
	       enddo
	       do i=1,Na5
	       a5b(i,ic)=a5b(i,ic)+a5aux(i,ic,imag,is)*akl(2,5)
	       enddo
	       do i=1,Na6
	       a6b(i,ic)=a6b(i,ic)+a6aux(i,ic,imag,is)*akl(2,6)
	       enddo
	       do i=1,Nb3
	       b3b(i,ic)=b3b(i,ic)+b3aux(i,ic,imag,is)*akl(1,3)
	       enddo
	       do i=1,Nb4
	       b4b(i,ic)=b4b(i,ic)+b4aux(i,ic,imag,is)*akl(1,4)
	       enddo
	       do i=1,Nb5
	       b5b(i,ic)=b5b(i,ic)+b5aux(i,ic,imag,is)*akl(1,5)
	       enddo
	       do i=1,Nb6
	       b6b(i,ic)=b6b(i,ic)+b6aux(i,ic,imag,is)*akl(1,6)
	       enddo
	       
 199           continue
               enddo
 200           continue
 
               close(1)
	       
c	       do imag=1,6
c	       do ic=1,8
c	       write(6,*) imag,ic,Nsmag(ic,imag),Nsmag(ic,imag)
c	       enddo
c	       enddo
 
               if(itot.ne.576) then
       write(6,*) "Tot. numb. of entries in tripD1D2.errors: ", itot
       write(6,*) "Warning some MQX, D1 or D2 errors are not defined"
       write(6,*)
               endif
	       
	       do ic=1,8
	       do imag=1,6
	       if(Nsmag(ic,imag).ne.Nsmag0(ic,imag).and.
     +            Nsmag(ic,imag).ne.0) then
	       write(6,*) 'Input twiss table not compatible with'
	       write(6,*) 'error readings:', ' ic=',ic,' imag= ',imag
	       stop
	       endif
	       enddo
	       enddo
	       
	       open(1,file='temp/MCX_setting.mad')
	       
C  A2 correction (local left /local right)
               
	       do ic=1,8
	       a2cor(ic)=-a2b(ic)/a2c(ic)
	       enddo
	       
	       write(1,*) '!! MQSX (a2) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KQSX3.L1 :=',a2cor(1),'/l.MQSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KQSX3.R1 :=',a2cor(2),'/l.MQSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KQSX3.L2 :=',a2cor(3),'/l.MQSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KQSX3.R2 :=',a2cor(4),'/l.MQSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KQSX3.L5 :=',a2cor(5),'/l.MQSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KQSX3.R5 :=',a2cor(6),'/l.MQSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KQSX3.L8 :=',a2cor(7),'/l.MQSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KQSX3.R8 :=',a2cor(8),'/l.MQSX ;'
               write(1,*)
	       
C  A3 correction (left / right cancellation of (0,3),(3,0) in 1/2/5 and 8)

	       do ic=1,8,2
	       det=-a3c(3,ic)*a3c(4,ic+1)+a3c(3,ic+1)*a3c(4,ic)
	       aux1=-a3b(3,ic)+a3b(3,ic+1)
	       aux2=-a3b(4,ic)+a3b(4,ic+1)
	       if(det.ne.0.) then
	       a3cor(ic)  =1.d0/det*(-a3c(4,ic+1)*aux1+a3c(3,ic+1)*aux2)
	       a3cor(ic+1)=1.d0/det*(-a3c(4,ic)*aux1+a3c(3,ic)*aux2)
	       else
	       a3cor(ic)  =0.0
	       a3cor(ic+1)=0.0
	       endif
	       enddo
	       
	       write(1,*) '!! MCSSX (a3) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSSX3.L1 :=',bv*a3cor(1),'/l.MCSSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSSX3.R1 :=',bv*a3cor(2),'/l.MCSSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSSX3.L2 :=',bv*a3cor(3),'/l.MCSSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSSX3.R2 :=',bv*a3cor(4),'/l.MCSSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSSX3.L5 :=',bv*a3cor(5),'/l.MCSSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSSX3.R5 :=',bv*a3cor(6),'/l.MCSSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSSX3.L8 :=',bv*a3cor(7),'/l.MCSSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSSX3.R8 :=',bv*a3cor(8),'/l.MCSSX ;'
               write(1,*)
              
	       
C  A4 correction (left / right cancellation of (1,3),(3,1) in 1/2/5 and 8)
               
	       do ic=1,8,2
	       det=a4c(1,ic)*a4c(2,ic+1)-a4c(1,ic+1)*a4c(2,ic)
	       aux1=-a4b(1,ic)-a4b(1,ic+1)
	       aux2=-a4b(2,ic)-a4b(2,ic+1)
	       if(det.ne.0.) then
	       a4cor(ic)  =1.d0/det*(a4c(2,ic+1)*aux1-a4c(1,ic+1)*aux2)
	       a4cor(ic+1)=1.d0/det*(-a4c(2,ic)*aux1+a4c(1,ic)*aux2)
	       else
	       a4cor(ic)  =0.0
	       a4cor(ic+1)=0.0
	       endif
	       enddo
	       
	       write(1,*) '!! MCOSX (a4) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOSX3.L1 :=',a4cor(1),'/l.MCOSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOSX3.R1 :=',a4cor(2),'/l.MCOSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOSX3.L2 :=',a4cor(3),'/l.MCOSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOSX3.R2 :=',a4cor(4),'/l.MCOSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOSX3.L5 :=',a4cor(5),'/l.MCOSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOSX3.R5 :=',a4cor(6),'/l.MCOSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOSX3.L8 :=',a4cor(7),'/l.MCOSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOSX3.R8 :=',a4cor(8),'/l.MCOSX ;'
               write(1,*)
	       
	       
C  A5 correction (left / right cancellation of (0,5),(5,0) in IR1 and IR5)

	       do ic=1,8,2
	       det=-a5c(5,ic)*a5c(6,ic+1)+a5c(5,ic+1)*a5c(6,ic)
	       aux1=-a5b(5,ic)+a5b(5,ic+1)
	       aux2=-a5b(6,ic)+a5b(6,ic+1)
	       if(det.ne.0.) then
	       a5cor(ic)  =1.d0/det*(-a5c(6,ic+1)*aux1+a5c(5,ic+1)*aux2)
	       a5cor(ic+1)=1.d0/det*(-a5c(6,ic)*aux1+a5c(5,ic)*aux2)
	       else
	       a5cor(ic)  =0.0
	       a5cor(ic+1)=0.0
	       endif
	       enddo
	       
	       write(1,*) '!! MCDSX (a5) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCDSX3.L1 :=',bv*a5cor(1),'/l.MCDSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCDSX3.R1 :=',bv*a5cor(2),'/l.MCDSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCDSX3.L5 :=',bv*a5cor(5),'/l.MCDSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCDSX3.R5 :=',bv*a5cor(6),'/l.MCDSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
               write(1,*)
              
	       
C  A6 correction (left / right cancellation of (5,1),(1,5) in IR1 and IR5)
               
	       do ic=1,8,2
	       det=a6c(1,ic)*a6c(2,ic+1)-a6c(1,ic+1)*a6c(2,ic)
	       aux1=-a6b(1,ic)-a6b(1,ic+1)
	       aux2=-a6b(2,ic)-a6b(2,ic+1)
	       if(det.ne.0.) then
	       a6cor(ic)  =1.d0/det*(a6c(2,ic+1)*aux1-a6c(1,ic+1)*aux2)
	       a6cor(ic+1)=1.d0/det*(-a6c(2,ic)*aux1+a6c(1,ic)*aux2)
	       else
	       a6cor(ic)  =0.0
	       a6cor(ic+1)=0.0
	       endif
	       enddo
	       
	       write(1,*) '!! MCTSX (a6) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTSX3.L1 :=',a6cor(1),'/l.MCTSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTSX3.R1 :=',a6cor(2),'/l.MCTSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTSX3.L5 :=',a6cor(5),'/l.MCTSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTSX3.R5 :=',a6cor(6),'/l.MCTSX3;'
               write(1,*)
	       
C  B3 correction (left / right cancellation of (1,2),(2,1) in 1/2/5 and 8)

c	       do ic=1,4,2
c	       det=b3c(5,ic)*b3c(6,ic+1)-b3c(5,ic+1)*b3c(6,ic)
c	       aux1=-b3b(5,ic)-b3b(5,ic+1)
c	       aux2=-b3b(6,ic)-b3b(6,ic+1)
c	       b3cor(ic)  =1.d0/det*(b3c(6,ic+1)*aux1-b3c(5,ic+1)*aux2)
c	       b3cor(ic+1)=1.d0/det*(-b3c(6,ic)*aux1+b3c(5,ic)*aux2)
c	       enddo
	       do ic=1,8,2
	       det=-b3c(3,ic)*b3c(4,ic+1)+b3c(3,ic+1)*b3c(4,ic)
	       aux1=-b3b(3,ic)+b3b(3,ic+1)
	       aux2=-b3b(4,ic)+b3b(4,ic+1)
	       if(det.ne.0.) then
	       b3cor(ic)  =1.d0/det*(-b3c(4,ic+1)*aux1+b3c(3,ic+1)*aux2)
	       b3cor(ic+1)=1.d0/det*(-b3c(4,ic)*aux1+b3c(3,ic)*aux2)
	       else
	       b3cor(ic)  =0.0
	       b3cor(ic+1)=0.0
	       endif
	       enddo
	       
	       
	       write(1,*) '!! MCSX (b3) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSX3.L1 :=',b3cor(1),'/l.MCSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSX3.R1 :=',b3cor(2),'/l.MCSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSX3.L2 :=',b3cor(3),'/l.MCSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSX3.R2 :=',b3cor(4),'/l.MCSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSX3.L5 :=',b3cor(5),'/l.MCSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSX3.R5 :=',b3cor(6),'/l.MCSX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSX3.L8 :=',b3cor(7),'/l.MCSX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCSX3.R8 :=',b3cor(8),'/l.MCSX ;'
               write(1,*)	       


C  B4 correction (left / right cancellation of (0,4),(4,0) in 1/2/5 and 8)
               
	       do ic=1,8,2
	       det=b4c(1,ic)*b4c(2,ic+1)-b4c(1,ic+1)*b4c(2,ic)
	       aux1=-b4b(1,ic)-b4b(1,ic+1)
	       aux2=-b4b(2,ic)-b4b(2,ic+1)
	       if(det.ne.0.) then
	       b4cor(ic)  =1.d0/det*(b4c(2,ic+1)*aux1-b4c(1,ic+1)*aux2)
	       b4cor(ic+1)=1.d0/det*(-b4c(2,ic)*aux1+b4c(1,ic)*aux2)
	       else
	       b4cor(ic)  =0.0
	       b4cor(ic+1)=0.0
	       endif
	       enddo
	       
	       write(1,*) '!! MCOX (b4) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOX3.L1 :=',bv*b4cor(1),'/l.MCOX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOX3.R1 :=',bv*b4cor(2),'/l.MCOX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOX3.L2 :=',bv*b4cor(3),'/l.MCOX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOX3.R2 :=',bv*b4cor(4),'/l.MCOX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOX3.L5 :=',bv*b4cor(5),'/l.MCOX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOX3.R5 :=',bv*b4cor(6),'/l.MCOX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOX3.L8 :=',bv*b4cor(7),'/l.MCOX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCOX3.R8 :=',bv*b4cor(8),'/l.MCOX ;'
               write(1,*)	       

C  B5 correction (left / right cancellation of (5,0),(0,5) in IR1 and IR5)

	       do ic=1,8,2
	       det=-b5c(1,ic)*b5c(2,ic+1)+b5c(1,ic+1)*b5c(2,ic)
	       aux1=-b5b(1,ic)+b5b(1,ic+1)
	       aux2=-b5b(2,ic)+b5b(2,ic+1)
	       if(det.ne.0.) then
	       b5cor(ic)  =1.d0/det*(-b5c(2,ic+1)*aux1+b5c(1,ic+1)*aux2)
	       b5cor(ic+1)=1.d0/det*(-b5c(2,ic)*aux1+b5c(1,ic)*aux2)
	       else
	       b5cor(ic)  =0.0
	       b5cor(ic+1)=0.0
	       endif
	       enddo
	       	       
	       write(1,*) '!! MCSX (b5) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCDX3.L1 :=',b5cor(1),'/l.MCDX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCDX3.R1 :=',b5cor(2),'/l.MCDX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCDX3.L5 :=',b5cor(5),'/l.MCDX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCDX3.R5 :=',b5cor(6),'/l.MCDX3;'
               write(1,*)	       


C  B6 correction (left / right cancellation of (6,0),(0,6) in 1/2/5 and 8)
	       
	       do ic=1,8,2
	       det=b6c(1,ic)*b6c(2,ic+1)-b6c(1,ic+1)*b6c(2,ic)
	       aux1=-b6b(1,ic)-b6b(1,ic+1)
	       aux2=-b6b(2,ic)-b6b(2,ic+1)
	       b6cor(ic)  =1.d0/det*(b6c(2,ic+1)*aux1-b6c(1,ic+1)*aux2)
	       b6cor(ic+1)=1.d0/det*(-b6c(2,ic)*aux1+b6c(1,ic)*aux2)
	       if(det.ne.0.) then
	       else
	       b6cor(ic)  =0.0
	       b6cor(ic+1)=0.0
	       endif
	       enddo
	       
	       
	       write(1,*) '!! MCTX (b6) corrector'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTX3.L1 :=',bv*b6cor(1),'/l.MCTX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTX3.R1 :=',bv*b6cor(2),'/l.MCTX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTX3.L2 :=',bv*b6cor(3),'/l.MCTX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTX3.R2 :=',bv*b6cor(4),'/l.MCTX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTX3.L5 :=',bv*b6cor(5),'/l.MCTX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTX3.R5 :=',bv*b6cor(6),'/l.MCTX3;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTX3.L8 :=',bv*b6cor(7),'/l.MCTX ;'
	       write(1,'(a12,1x,e14.6,1x,a10)')
     +         'KCTX3.R8 :=',bv*b6cor(8),'/l.MCTX ;'
               write(1,*)	       

	       write(1,*) 'return;'
	       
	       close(1)
	       	       	       
	       ICHECK=1
	       if(icheck.eq.1) then
	       write(6,*) 'A2, (1,-1) resonnance driving terms'
	       do ic=1,8
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a2b(ic)+a2c(ic)*a2cor(ic)
	       aux2=aux2+a2b(ic)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A2_(1,-1)',ic,aux2,aux1
	       enddo
	       write(6,*)
	       write(6,*) 'A3, (2,1) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a3b(1,ic)+a3c(1,ic)*a3cor(ic)-
     +                   a3b(1,ic+1)-a3c(1,ic+1)*a3cor(ic+1)
	       aux2=aux2+a3b(1,ic)-a3b(1,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A3_(2,1)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A3, (1,2) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a3b(2,ic)+a3c(2,ic)*a3cor(ic)-
     +                   a3b(2,ic+1)-a3c(2,ic+1)*a3cor(ic+1)	       
	       aux2=aux2+a3b(2,ic)-a3b(2,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A3_(1,2)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A3, (0,3) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a3b(3,ic)+a3c(3,ic)*a3cor(ic)-
     +                   a3b(3,ic+1)-a3c(3,ic+1)*a3cor(ic+1)	       
	       aux2=aux2+a3b(3,ic)-a3b(3,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A3_(0,3)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A3, (3,0) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a3b(4,ic)+a3c(4,ic)*a3cor(ic)-
     +                   a3b(4,ic+1)-a3c(4,ic+1)*a3cor(ic+1)	       
	       aux2=aux2+a3b(4,ic)-a3b(4,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A3_(3,0)',ic,aux2,aux1
	       enddo
	       write(6,*)
	       write(6,*) 'A4, (1,3) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a4b(1,ic)+a4c(1,ic)*a4cor(ic)+
     +                   a4b(1,ic+1)+a4c(1,ic+1)*a4cor(ic+1)	       
	       aux2=aux2+a4b(1,ic)+a4b(1,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A4_(1,3)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A4, (3,1) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a4b(2,ic)+a4c(2,ic)*a4cor(ic)+
     +                   a4b(2,ic+1)+a4c(2,ic+1)*a4cor(ic+1)	       
	       aux2=aux2+a4b(2,ic)+a4b(2,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A4_(3,1)',ic,aux2,aux1
	       enddo
	       write(6,*)
	       write(6,*) 'A5, (4,1) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a5b(1,ic)+a5c(1,ic)*a5cor(ic)-
     +                   a5b(1,ic+1)-a5c(1,ic+1)*a5cor(ic+1)
	       aux2=aux2+a5b(1,ic)-a5b(1,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A5_(4,1)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A5, (1,4) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a5b(2,ic)+a5c(2,ic)*a5cor(ic)-
     +                   a5b(2,ic+1)-a5c(2,ic+1)*a5cor(ic+1)
	       aux2=aux2+a5b(2,ic)-a5b(2,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A5_(1,4)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A5, (2,3) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a5b(3,ic)+a5c(3,ic)*a5cor(ic)-
     +                   a5b(3,ic+1)-a5c(3,ic+1)*a5cor(ic+1)
	       aux2=aux2+a5b(3,ic)-a5b(3,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A5_(2,3)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A5, (3,2) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a5b(4,ic)+a5c(4,ic)*a5cor(ic)-
     +                   a5b(4,ic+1)-a5c(4,ic+1)*a5cor(ic+1)
	       aux2=aux2+a5b(4,ic)-a5b(4,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A5_(3,2)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A5, (0,5) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a5b(5,ic)+a5c(5,ic)*a5cor(ic)-
     +                   a5b(5,ic+1)-a5c(5,ic+1)*a5cor(ic+1)
	       aux2=aux2+a5b(5,ic)-a5b(5,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A5_(0,5)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A5, (5,0) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a5b(6,ic)+a5c(6,ic)*a5cor(ic)-
     +                   a5b(6,ic+1)-a5c(6,ic+1)*a5cor(ic+1)
	       aux2=aux2+a5b(6,ic)-a5b(6,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A5_(5,0)',ic,aux2,aux1
	       enddo
	       write(6,*)
	       write(6,*) 'A6, (5,1) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a6b(1,ic)+a6c(1,ic)*a6cor(ic)+
     +                   a6b(1,ic+1)+a6c(1,ic+1)*a6cor(ic+1)	       
	       aux2=aux2+a6b(1,ic)+a6b(1,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A6_(5,1)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A6, (1,5) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a6b(2,ic)+a6c(2,ic)*a6cor(ic)+
     +                   a6b(2,ic+1)+a6c(2,ic+1)*a6cor(ic+1)	       
	       aux2=aux2+a6b(2,ic)+a6b(2,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A6_(1,5)',ic,aux2,aux1
	       enddo
	       write(6,*) 'A6, (3,3) resonnance driving terms'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+a6b(3,ic)+a6c(3,ic)*a6cor(ic)+
     +                   a6b(3,ic+1)+a6c(3,ic+1)*a6cor(ic+1)	       
	       aux2=aux2+a6b(3,ic)+a6b(3,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'A6_(3,3)',ic,aux2,aux1
	       enddo
	       write(6,*)
	       write(6,*) 'B3, (3,0) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b3b(1,ic)+b3c(1,ic)*b3cor(ic)-
     +                   b3b(1,ic+1)-b3c(1,ic+1)*b3cor(ic+1)
	       aux2=aux2+b3b(1,ic)-b3b(1,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B3_(3,0)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B3, (0,3) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b3b(2,ic)+b3c(2,ic)*b3cor(ic)-
     +                   b3b(2,ic+1)-b3c(2,ic+1)*b3cor(ic+1)	       
	       aux2=aux2+b3b(2,ic)-b3b(2,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B3_(0,3)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B3, (1,2) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b3b(3,ic)+b3c(3,ic)*b3cor(ic)-
     +                   b3b(3,ic+1)-b3c(3,ic+1)*b3cor(ic+1)	       
	       aux2=aux2+b3b(3,ic)-b3b(3,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B3_(1,2)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B3, (2,1) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b3b(4,ic)+b3c(4,ic)*b3cor(ic)-
     +                   b3b(4,ic+1)-b3c(4,ic+1)*b3cor(ic+1)	       
	       aux2=aux2+b3b(4,ic)-b3b(4,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B3_(2,1)',ic,aux2,aux1
	       enddo
	       write(6,*)
	       write(6,*) 'B4, (4,0) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       anorm=1.d0/32.d0/2.d0/asin(1.0d0)*100.d0*5.03d-10
	       aux1=aux1+b4b(1,ic)+b4c(1,ic)*b4cor(ic)+
     +                   b4b(1,ic+1)+b4c(1,ic+1)*b4cor(ic+1)	       
	       aux2=aux2+b4b(1,ic)+b4b(1,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B4_(4,0)',ic,aux2*anorm,aux1*anorm
	       enddo
	       write(6,*) 'B4, (0,4) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       anorm=1.d0/32.d0/2.d0/asin(1.0d0)*100.d0*5.03d-10
	       aux1=aux1+b4b(2,ic)+b4c(2,ic)*b4cor(ic)+
     +                   b4b(2,ic+1)+b4c(2,ic+1)*b4cor(ic+1)	       
	       aux2=aux2+b4b(2,ic)+b4b(2,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B4_(0,4)',ic,aux2*anorm,aux1*anorm
	       enddo
	       write(6,*) 'B4, (2,2) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       anorm=1.d0/32.d0/2.d0/asin(1.0d0)*100.d0*5.03d-10
	       aux1=aux1+b4b(3,ic)+b4c(3,ic)*b4cor(ic)+
     +                   b4b(3,ic+1)+b4c(3,ic+1)*b4cor(ic+1)	       
	       aux2=aux2+b4b(3,ic)+b4b(3,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B4_(2,2)',ic,2.0d0*aux2*anorm,2.0d0*aux1*anorm
	       enddo
	       write(6,*)
	       write(6,*) 'B5, (5,0) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b5b(1,ic)+b5c(1,ic)*b5cor(ic)-
     +                   b5b(1,ic+1)-b5c(1,ic+1)*b5cor(ic+1)
	       aux2=aux2+b5b(1,ic)-b5b(1,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B5_(5,0)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B5, (0,5) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b5b(2,ic)+b5c(2,ic)*b5cor(ic)-
     +                   b5b(2,ic+1)-b5c(2,ic+1)*b5cor(ic+1)
	       aux2=aux2+b5b(2,ic)-b5b(2,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B5_(0,5)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B5, (3,2) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b5b(3,ic)+b5c(3,ic)*b5cor(ic)-
     +                   b5b(3,ic+1)-b5c(3,ic+1)*b5cor(ic+1)
	       aux2=aux2+b5b(3,ic)-b5b(3,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B5_(3,2)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B5, (2,3) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b5b(4,ic)+b5c(4,ic)*b5cor(ic)-
     +                   b5b(4,ic+1)-b5c(4,ic+1)*b5cor(ic+1)
	       aux2=aux2+b5b(4,ic)-b5b(4,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B5_(2,3)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B5, (1,4) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b5b(5,ic)+b5c(5,ic)*b5cor(ic)-
     +                   b5b(5,ic+1)-b5c(5,ic+1)*b5cor(ic+1)
	       aux2=aux2+b5b(5,ic)-b5b(5,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B5_(1,4)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B5, (4,1) resonnance driving terms (beam2)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b5b(6,ic)+b5c(6,ic)*b5cor(ic)-
     +                   b5b(6,ic+1)-b5c(6,ic+1)*b5cor(ic+1)
	       aux2=aux2+b5b(6,ic)-b5b(6,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B5_(4,1)',ic,aux2,aux1
	       enddo
	       write(6,*)
	       write(6,*) 'B6, (6,0) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b6b(1,ic)+b6c(1,ic)*b6cor(ic)+
     +                   b6b(1,ic+1)+b6c(1,ic+1)*b6cor(ic+1)	       
	       aux2=aux2+b6b(1,ic)+b6b(1,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B6_(6,0)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B6, (0,6) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b6b(2,ic)+b6c(2,ic)*b6cor(ic)+
     +                   b6b(2,ic+1)+b6c(2,ic+1)*b6cor(ic+1)	       
	       aux2=aux2+b6b(2,ic)+b6b(2,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B6_(0,6)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B6, (4,2) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b6b(3,ic)+b6c(3,ic)*b6cor(ic)+
     +                   b6b(3,ic+1)+b6c(3,ic+1)*b6cor(ic+1)	       
	       aux2=aux2+b6b(3,ic)+b6b(3,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B6_(4,2)',ic,aux2,aux1
	       enddo
	       write(6,*) 'B6, (2,4) resonnance driving terms (beam1)'
	       do ic=1,8,2
	       aux1=0.0d0
	       aux2=0.0d0
	       aux1=aux1+b6b(4,ic)+b6c(4,ic)*b6cor(ic)+
     +                   b6b(4,ic+1)+b6c(4,ic+1)*b6cor(ic+1)	       
	       aux2=aux2+b6b(4,ic)+b6b(4,ic+1)
	       write(6,'(a10,1x,i2,1x,2(e12.4,1x))')
     +         'B6_(2,4)',ic,aux2,aux1
	       enddo
	       
	       endif
	       
	        
              stop
	      end
	      
	       
	       
	       
