ccccc Author : S. Fartoukh
ccccc Version: 23 June 2010
ccccc 2011/11/22 from SLHCV3.0 of 2011/07/27
ccccc Riccardo De Maria
ccccc 1 December 2014 adapting for MBH and missing MCO, MCD
ccccc 25 April 2016 adapting for missing MSS new sequence

      program corr_MB

      implicit none
      !integer Ns_MB,Ns_MB0
      integer Ns_MB
      parameter (Ns_MB=10)

      real*8 b2c(2,2,8),b2b(2,8),b2(2,8)
      real*8 a2c(2,8),a2b(2,8),a2(8),a2loc(8),a2res(2),a2c_aux(2,8)
      real*8 a3c(2,8),a3b(2,8),a3(8),a3loc(8),a3res(2),a3c_aux(2,8)
      real*8 b3b(8),b3(8),b4b(8),b4(8),b5b(8),b5(8)
      real*8 b2aux(2,8,Ns_MB*154),a2aux(2,8,Ns_MB*154),
     +    a3aux(2,8,Ns_MB*154)
      real*8 Ba2(8,2),Ba3(8,2),akaux(2,11)
      real*8 kqtf(8),kqtd(8)
      real*8 alpha,betx,bety,dx,amu,amux,amuy,cosi,sinu,aux1,aux2
      real*8 twopi,k1lmqt,aL_MQS,aL_MQT
      real*8 kLMCSmax,kLMCOmax,kLMCDmax
      real*8 Rr,anorm,signb,dq
      integer imb(8),imqs(8),imqtf(8),imqtd(8)
      integer imco(8),imcd(8),imcs(8)
      integer i,j,k,isec,ibeam,iaux,bv,isec0
      integer imqnum,imqpol
      character*20 chardum
      character*20 f1,f2,f3,f4
      real*8 energy

      bv=0
      isec0=0

      kLMCSmax=0.110*0.471*2 /0.017**2*0.3/7000.
      kLMCOmax=0.066*0.040*6 /0.017**3*0.3/7000.
      kLMCDmax=0.066*0.100*24/0.017**4*0.3/7000.

      twopi=4*asin(1.)
      aL_MQS=0.32
      aL_MQT=0.32
c      alpha=twopi/1232.
      Rr=0.017

      do i=1,2
        a2res(i)=0.
        a3res(i)=0.
      enddo

      do i=1,8
        imb(i)=0
        imqs(i)=0
        imqtf(i)=0
        imqtd(i)=0
        imco(i)=0
        imcs(i)=0
        imcd(i)=0
        a2(i)=0.
        a3(i)=0.
        a2loc(i)=0.
        a3loc(i)=0.
        b3b(i)=0.
        b3(i)=0.
        b4b(i)=0.
        b4(i)=0.
        b5b(i)=0.
        b5(i)=0.
      enddo

      do i=1,2
        do j=1,8
          a2c(i,j)=0.
          a2b(i,j)=0.
          a3c(i,j)=0.
          a3b(i,j)=0.
        enddo
      enddo

      do i=1,2
        do j=1,2
          do k=1,8
            b2c(i,j,k)=0.0
          enddo
        enddo
      enddo

      do j=1,2
        do k=1,8
          b2(j,k)=0.
          b2b(j,k)=0.
        enddo
      enddo


      do i=1,2
        do j=1,8
          do k=1,Ns_MB*154
            b2aux(i,j,k)=0.0
            a2aux(i,j,k)=0.0
            a3aux(i,j,k)=0.0
          enddo
        enddo
      enddo

      do i=1,8
        kqtf(i)=0.d0
        kqtd(i)=0.d0
      enddo

      open(1,file='temp/optics0_MB.mad')
      open(2,file='temp/MB.errors')

      do while(.true.)
        read(1,*,err=110,end=111) f1,f2,f3,f4
        if (f2.eq."ENERGY") then
           read(f4,'(f10.0)') energy
           goto 111
        endif
110     continue
      enddo
111   continue

      write(*,*) "Energy is",energy,"GeV"


      do while(.true.)
        read(1,*,err=99,end=100) chardum,alpha,k1lmqt,
     +                         betx,bety,dx,amux,amuy
        aux1=sqrt(betx*bety)
        aux2=sqrt(betx*bety)*dx
        amux=twopi*amux
        amuy=twopi*amuy
        amu=amux-amuy
        cosi=cos(amu)
        sinu=sin(amu)
        if(INDEX(chardum,"R1.B").ne.0.or.
     +       INDEX(chardum,"L2.B").ne.0) then
        isec=1
        elseif(INDEX(chardum,"R2.B").ne.0.or.
     +       INDEX(chardum,"L3.B").ne.0) then
        isec=2
        elseif(INDEX(chardum,"R3.B").ne.0.or.
     +       INDEX(chardum,"L4.B").ne.0) then
        isec=3
        elseif(INDEX(chardum,"R4.B").ne.0.or.
     +       INDEX(chardum,"L5.B").ne.0) then
        isec=4
        elseif(INDEX(chardum,"R5.B").ne.0.or.
     +       INDEX(chardum,"L6.B").ne.0) then
        isec=5
        elseif(INDEX(chardum,"R6.B").ne.0.or.
     +       INDEX(chardum,"L7.B").ne.0) then
        isec=6
        elseif(INDEX(chardum,"R7.B").ne.0.or.
     +       INDEX(chardum,"L8.B").ne.0) then
        isec=7
        elseif(INDEX(chardum,"R8.B").ne.0.or.
     +       INDEX(chardum,"L1.B").ne.0) then
        isec=8
        endif
        if(INDEX(chardum,"MB.").ne.0.or.
     +      INDEX(chardum,"MBH.").ne.0) then
          if(INDEX(chardum,".B1").ne.0) ibeam=1
          if(INDEX(chardum,".B2").ne.0) ibeam=2

          if(isec0.eq.0) isec0=isec
          if(isec.eq.isec0+1) then
            bv=bv+1
          elseif(isec.eq.isec0-1) then
            bv=bv-1
          endif
          isec0=isec

          imb(isec)=imb(isec)+1
          iaux=imb(isec)
          b2aux(1,isec,iaux)=betx
          b2aux(2,isec,iaux)=bety
          a2aux(1,isec,iaux)=aux1*cosi
          a2aux(2,isec,iaux)=aux1*sinu
          a3aux(1,isec,iaux)=aux2*cosi
          a3aux(2,isec,iaux)=aux2*sinu
        elseif(INDEX(chardum,"MQS.").ne.0) then
          imqs(isec)=imqs(isec)+1
          a2c(1,isec)=a2c(1,isec)+aux1*cosi/twopi*aL_MQS
          a2c(2,isec)=a2c(2,isec)+aux1*sinu/twopi*aL_MQS
        elseif(INDEX(chardum,"MCO.").ne.0) then
          imco(isec)=imco(isec)+1
        elseif(INDEX(chardum,"MCD.").ne.0) then
          imcd(isec)=imcd(isec)+1
        elseif(INDEX(chardum,"MCS.").ne.0) then
          imcs(isec)=imcs(isec)+1
        elseif(INDEX(chardum,"MSS.").ne.0) then
          a3c(1,isec)=a3c(1,isec)+aux2*cosi/twopi
          a3c(2,isec)=a3c(2,isec)+aux2*sinu/twopi
        elseif(INDEX(chardum,"MQT.").ne.0) then
c         Test polarity of MQT not based on betx>bety
          read( chardum(5:7),'(i2)') imqnum
          imqpol=1
          if (mod(isec,2).eq.0) imqpol=-imqpol
          if (mod(imqnum,2 ).eq.0) imqpol=-imqpol
          if (ibeam.eq.2)       imqpol=-imqpol
c          if ((betx.gt.bety).and.(imqpol.eq.-1))   write(*,*),
c     +         isec,imqnum, betx.gt.bety,imqpol
c          if (betx.gt.bety) then
          !write(*,*) chardum, imqpol
          if (imqpol.eq.1) then
            b2c(1,1,isec)=b2c(1,1,isec)+betx/2./twopi*aL_MQT
            b2c(2,1,isec)=b2c(2,1,isec)-bety/2./twopi*aL_MQT
            imqtf(isec)=imqtf(isec)+1
            kqtf(isec)=k1lmqt/aL_MQT
          else
            b2c(1,2,isec)=b2c(1,2,isec)+betx/2./twopi*aL_MQT
            b2c(2,2,isec)=b2c(2,2,isec)-bety/2./twopi*aL_MQT
            imqtd(isec)=imqtd(isec)+1
            kqtd(isec)=k1lmqt/aL_MQT
          endif
        endif
 99   continue
      enddo
 100  continue
c        End of optics file reading

      do isec=1,8
        do i=1,2
           a2c(i,isec)=a2c(i,isec)*4./imqs(isec)
           b2c(i,1,isec)=b2c(i,1,isec)*8./imqtf(isec)
           b2c(i,2,isec)=b2c(i,2,isec)*8./imqtd(isec)
         enddo
         kqtf(isec)=kqtf(isec)*imqtf(isec)/8.
         kqtd(isec)=kqtd(isec)*imqtd(isec)/8.
      enddo

      if(ibeam.eq.2.and.bv.lt.0) ibeam=4

       !Ns_MB0=imb(1)/154
       do i=1,8
         !if(imb(i).ne.Ns_MB0*154) then
         !write(6,*) imb(i),' dipoles in sector ',i
         !write(6,*) 'File optics0_MB.mad corrupted'
         !stop
         !else
       write(6,*) '******Sector****** ',i,mod(i,8)+1
       write(6,'(i4,1x,a30,1x,i1)') imb(i),  ' MB   slices in sector ',i
       write(6,'(i4,1x,a30,1x,i1)') imqtf(i),' MQTF slices in sector ',i
       write(6,'(i4,1x,a30,1x,i1)') imqtd(i),' MQTD slices in sector ',i
       write(6,'(i4,1x,a30,1x,i1)') imqs(i) ,' MQS  slices in sector ',i
       write(6,'(i4,1x,a30,1x,i1)') imcs(i) ,' MCS  slices in sector ',i
       write(6,'(i4,1x,a30,1x,i1)') imco(i) ,' MCO  slices in sector ',i
       write(6,'(i4,1x,a30,1x,i1)') imcd(i) ,' MCD  slices in sector ',i
         !endif
         imb(i)=0
       enddo

       do while(.true.)
         read(2,*,err=101,end=102)
     +       chardum,(akaux(1,j),akaux(2,j),j=1,11)
         if(INDEX(chardum,"R1.B").ne.0.or.
     +      INDEX(chardum,"L2.B").ne.0) then
           isec=1
         elseif(INDEX(chardum,"R2.B").ne.0.or.
     +          INDEX(chardum,"L3.B").ne.0) then
           isec=2
         elseif(INDEX(chardum,"R3.B").ne.0.or.
     +          INDEX(chardum,"L4.B").ne.0) then
           isec=3
         elseif(INDEX(chardum,"R4.B").ne.0.or.
     +          INDEX(chardum,"L5.B").ne.0) then
           isec=4
         elseif(INDEX(chardum,"R5.B").ne.0.or.
     +          INDEX(chardum,"L6.B").ne.0) then
           isec=5
         elseif(INDEX(chardum,"R6.B").ne.0.or.
     +          INDEX(chardum,"L7.B").ne.0) then
           isec=6
         elseif(INDEX(chardum,"R7.B").ne.0.or.
     +          INDEX(chardum,"L8.B").ne.0) then
           isec=7
         elseif(INDEX(chardum,"R8.B").ne.0.or.
     +          INDEX(chardum,"L1.B").ne.0) then
           isec=8
         endif
         imb(isec)=imb(isec)+1
         iaux=imb(isec)
         b2b(1,isec)=b2b(1,isec)+b2aux(1,isec,iaux)*akaux(1,2)/2./twopi
         b2b(2,isec)=b2b(2,isec)-b2aux(2,isec,iaux)*akaux(1,2)/2./twopi
         a2b(1,isec)=a2b(1,isec)+a2aux(1,isec,iaux)*akaux(2,2)/twopi
         a2b(2,isec)=a2b(2,isec)+a2aux(2,isec,iaux)*akaux(2,2)/twopi
         a3b(1,isec)=a3b(1,isec)+a3aux(1,isec,iaux)*akaux(2,3)/twopi
         a3b(2,isec)=a3b(2,isec)+a3aux(2,isec,iaux)*akaux(2,3)/twopi
         b3b(isec)=b3b(isec)+akaux(1,3)
         b4b(isec)=b4b(isec)+akaux(1,4)
         b5b(isec)=b5b(isec)+akaux(1,5)
 101     continue
       enddo
 102   continue

       !do i=1,8
       !if(imb(i).ne.Ns_MB0*154) then
       !write(6,*) imb(i),' dipoles in sector ',i
       !write(6,*) 'File MB.errors corrupted'
       !stop
       !endif
       !enddo


       close(1)
       close(2)

C First correction

       do isec=1,8
C b2
        anorm=b2c(1,1,isec)*b2c(2,2,isec)-b2c(1,2,isec)*b2c(2,1,isec)
        b2(1,isec)=b2c(2,2,isec)*b2b(1,isec)-b2c(1,2,isec)*b2b(2,isec)
        b2(2,isec)=b2c(1,1,isec)*b2b(2,isec)-b2c(2,1,isec)*b2b(1,isec)
        b2(1,isec)=-b2(1,isec)/anorm
        b2(2,isec)=-b2(2,isec)/anorm

C a2
       anorm=0.
       do i=1,2
       a2loc(isec)=a2loc(isec)-a2c(i,isec)*a2b(i,isec)
       anorm=anorm+a2c(i,isec)**2
       enddo
       a2loc(isec)=a2loc(isec)/anorm
       do i=1,2
       a2res(i)=a2res(i)+a2loc(isec)*a2c(i,isec)+a2b(i,isec)
       enddo

C b3,b4,b5
       b3(isec)=-b3b(isec)/imcs(isec)
       b4(isec)=-b4b(isec)/imco(isec)
       b5(isec)=-b5b(isec)/imcd(isec)

C a3
       anorm=0.
       do i=1,2
       a3loc(isec)=a3loc(isec)-a3c(i,isec)*a3b(i,isec)
       anorm=anorm+a3c(i,isec)**2
       enddo
       if (anorm.gt.0) then
         a3loc(isec)=a3loc(isec)/anorm
       else
         a3loc(isec)=0
       endif
       do i=1,2
       a3res(i)=a3res(i)+a3loc(isec)*a3c(i,isec)+a3b(i,isec)
       enddo
c       write(*,*) a3res(1),a3res(2),isec
       enddo


C Check possible saturation of the spools at high energy

       if(energy.le.1000) then
       write(6,*) "Injection Energy"
       else
           write(6,*) "Collision energy"
       do isec=1,8
       if(abs(b3(isec)).gt.kLMCSmax)
     +     b3(isec)=b3(isec)/abs(b3(isec))*kLMCSmax
       if(abs(b4(isec)).gt.kLMCOmax)
     +     b4(isec)=b4(isec)/abs(b4(isec))*kLMCOmax
       if(abs(b5(isec)).gt.kLMCDmax)
     +     b5(isec)=b5(isec)/abs(b5(isec))*kLMCDmax
       enddo
       endif



C Second correction for a2 and a3

       open(1,file='temp/MB_corr_setting.mad')
       write(1,*) 'option,-echo;'
       write(1,*)

C MQS and MSS of sectors 81/12/45/56 are no longer global coupling correctors

       !do i=1,2
       !a2c_aux(i,1)=a2c(i,1)
       !a2c_aux(i,4)=a2c(i,4)
       !a2c_aux(i,5)=a2c(i,5)
       !a2c_aux(i,8)=a2c(i,8)
       !a3c_aux(i,1)=a3c(i,1)
       !a3c_aux(i,4)=a3c(i,4)
       !a3c_aux(i,5)=a3c(i,5)
       !a3c_aux(i,8)=a3c(i,8)
       !a2c(i,1)=0.d0
       !a2c(i,4)=0.d0
       !a2c(i,5)=0.d0
       !a2c(i,8)=0.d0
       !a3c(i,1)=0.d0
       !a3c(i,4)=0.d0
       !a3c(i,5)=0.d0
       !a3c(i,8)=0.d0
       !enddo

       call MINN(a2c,2,Ba2)
       call MINN(a3c,2,Ba3)
       !do i=1,2
       !a2c(i,1)=a2c_aux(i,1)
       !a2c(i,4)=a2c_aux(i,4)
       !a2c(i,5)=a2c_aux(i,5)
       !a2c(i,8)=a2c_aux(i,8)
       !a3c(i,1)=a3c_aux(i,1)
       !a3c(i,4)=a3c_aux(i,4)
       !a3c(i,5)=a3c_aux(i,5)
       !a3c(i,8)=a3c_aux(i,8)
       !enddo

C a2
       do isec=1,8
       a2(isec)=a2loc(isec)
       do j=1,2
       a2(isec)=a2(isec)+Ba2(isec,j)*a2res(j)
       enddo
       enddo
       do i=1,2
       a2res(i)=0.
       do isec=1,8
       a2res(i)=a2res(i)+a2(isec)*a2c(i,isec)+a2b(i,isec)
       enddo
       enddo

C a3
       do isec=1,8
       a3(isec)=a3loc(isec)
       do j=1,2
       a3(isec)=a3(isec)+Ba3(isec,j)*a3res(j)
       enddo
       enddo
       do i=1,2
       a3res(i)=0.
       do isec=1,8
       a3res(i)=a3res(i)+a3(isec)*a3c(i,isec)+a3b(i,isec)
       enddo
       enddo


CPrintout b2 correction

       if(ibeam.eq.1) signb= 1.
       if(ibeam.eq.2) signb=-1.
       if(ibeam.eq.4) signb= 1.
       write(1,*) '!!! b2-correction for beam',ibeam
       if(ibeam.eq.1) then
       write(1,*) 'kqtf.b1:=0;'
       write(1,*) 'kqtd.b1:=0;'
       write(1,'(a16,e20.10,a2)')'dKQTF.a12B1 := ',signb*b2(1,1),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a23B1 := ',signb*b2(1,2),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a34B1 := ',signb*b2(1,3),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a45B1 := ',signb*b2(1,4),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a56B1 := ',signb*b2(1,5),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a67B1 := ',signb*b2(1,6),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a78B1 := ',signb*b2(1,7),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a81B1 := ',signb*b2(1,8),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a12B1 := ',signb*b2(2,1),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a23B1 := ',signb*b2(2,2),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a34B1 := ',signb*b2(2,3),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a45B1 := ',signb*b2(2,4),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a56B1 := ',signb*b2(2,5),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a67B1 := ',signb*b2(2,6),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a78B1 := ',signb*b2(2,7),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a81B1 := ',signb*b2(2,8),';'
       write(1,*)
       write(1,'(a16,e20.10,a30)')
     +    'KQTF.a12B1  := ',kqtf(1) ,' + dKQTF.a12B1 - 1.0*kqtf.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a23B1  := ',kqtf(2) ,' + dKQTF.a23B1 + 3.0*kqtf.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a34B1  := ',kqtf(3) ,' + dKQTF.a34B1 + 3.0*kqtf.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a45B1  := ',kqtf(4) ,' + dKQTF.a45B1 - 1.0*kqtf.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a56B1  := ',kqtf(5) ,' + dKQTF.a56B1 - 1.0*kqtf.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a67B1  := ',kqtf(6) ,' + dKQTF.a67B1 + 3.0*kqtf.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a78B1  := ',kqtf(7) ,' + dKQTF.a78B1 + 3.0*kqtf.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a81B1  := ',kqtf(8) ,' + dKQTF.a81B1 - 1.0*kqtf.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a12B1  := ',kqtd(1) ,' + dKQTD.a12B1 - 1.0*kqtd.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a23B1  := ',kqtd(2) ,' + dKQTD.a23B1 + 3.0*kqtd.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a34B1  := ',kqtd(3) ,' + dKQTD.a34B1 + 3.0*kqtd.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a45B1  := ',kqtd(4) ,' + dKQTD.a45B1 - 1.0*kqtd.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a56B1  := ',kqtd(5) ,' + dKQTD.a56B1 - 1.0*kqtd.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a67B1  := ',kqtd(6) ,' + dKQTD.a67B1 + 3.0*kqtd.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a78B1  := ',kqtd(7) ,' + dKQTD.a78B1 + 3.0*kqtd.b1;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a81B1  := ',kqtd(8) ,' + dKQTD.a81B1 - 1.0*kqtd.b1;'
           elseif(ibeam.eq.2.or.ibeam.eq.4) then
       write(1,*) 'kqtf.b2:=0;'
       write(1,*) 'kqtd.b2:=0;'
       write(1,'(a16,e20.10,a2)')'dKQTF.a12B2 := ',signb*b2(1,1),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a23B2 := ',signb*b2(1,2),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a34B2 := ',signb*b2(1,3),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a45B2 := ',signb*b2(1,4),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a56B2 := ',signb*b2(1,5),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a67B2 := ',signb*b2(1,6),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a78B2 := ',signb*b2(1,7),';'
       write(1,'(a16,e20.10,a2)')'dKQTF.a81B2 := ',signb*b2(1,8),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a12B2 := ',signb*b2(2,1),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a23B2 := ',signb*b2(2,2),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a34B2 := ',signb*b2(2,3),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a45B2 := ',signb*b2(2,4),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a56B2 := ',signb*b2(2,5),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a67B2 := ',signb*b2(2,6),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a78B2 := ',signb*b2(2,7),';'
       write(1,'(a16,e20.10,a2)')'dKQTD.a81B2 := ',signb*b2(2,8),';'
       write(1,*)
       write(1,'(a16,e20.10,a30)')
     +    'KQTF.a12B2  := ',kqtf(1) ,' + dKQTF.a12B2 - 1.0*kqtf.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a23B2  := ',kqtf(2) ,' + dKQTF.a23B2 + 3.0*kqtf.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a34B2  := ',kqtf(3) ,' + dKQTF.a34B2 + 3.0*kqtf.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a45B2  := ',kqtf(4) ,' + dKQTF.a45B2 - 1.0*kqtf.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a56B2  := ',kqtf(5) ,' + dKQTF.a56B2 - 1.0*kqtf.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a67B2  := ',kqtf(6) ,' + dKQTF.a67B2 + 3.0*kqtf.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a78B2  := ',kqtf(7) ,' + dKQTF.a78B2 + 3.0*kqtf.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTF.a81B2  := ',kqtf(8) ,' + dKQTF.a81B2 - 1.0*kqtf.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a12B2  := ',kqtd(1) ,' + dKQTD.a12B2 - 1.0*kqtd.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a23B2  := ',kqtd(2) ,' + dKQTD.a23B2 + 3.0*kqtd.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a34B2  := ',kqtd(3) ,' + dKQTD.a34B2 + 3.0*kqtd.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a45B2  := ',kqtd(4) ,' + dKQTD.a45B2 - 1.0*kqtd.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a56B2  := ',kqtd(5) ,' + dKQTD.a56B2 - 1.0*kqtd.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a67B2  := ',kqtd(6) ,' + dKQTD.a67B2 + 3.0*kqtd.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a78B2  := ',kqtd(7) ,' + dKQTD.a78B2 + 3.0*kqtd.b2;'
           write(1,'(a16,e20.10,a30)')
     +    'KQTD.a81B2  := ',kqtd(8) ,' + dKQTD.a81B2 - 1.0*kqtd.b2;'
       endif
          write(1,*)

CPrintout a2 correction

       if(ibeam.eq.1) signb= 1.
       if(ibeam.eq.2) signb=-1.
       if(ibeam.eq.4) signb=-1.
       write(1,*) '!!! a2-correction for beam',ibeam
       write(1,'(a15)') 'CMRSKEW=0.;'
       write(1,'(a15)') 'CMISKEW=0.;'
      write(1,'(a15,1x,e14.8,1x,a1)')'B11 :=        ',signb*Ba2(1,1),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B12 :=        ',signb*Ba2(1,2),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B21 :=        ',signb*Ba2(2,1),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B22 :=        ',signb*Ba2(2,2),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B31 :=        ',signb*Ba2(3,1),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B32 :=        ',signb*Ba2(3,2),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B41 :=        ',signb*Ba2(4,1),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B42 :=        ',signb*Ba2(4,2),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B51 :=        ',signb*Ba2(5,1),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B52 :=        ',signb*Ba2(5,2),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B61 :=        ',signb*Ba2(6,1),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B62 :=        ',signb*Ba2(6,2),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B71 :=        ',signb*Ba2(7,1),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B72 :=        ',signb*Ba2(7,2),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B81 :=        ',signb*Ba2(8,1),';'
      write(1,'(a15,1x,e14.8,1x,a1)')'B82 :=        ',signb*Ba2(8,2),';'
      write(1,*)

c       if(ibeam.eq.4) then
c       dq=64.28000009-59.31000127
c       do isec=1,8
c       aux1= Ba2(isec,1)*cos(twopi*dq)+Ba2(isec,2)*sin(twopi*dq)
c       aux2= Ba2(isec,1)*sin(twopi*dq)-Ba2(isec,2)*cos(twopi*dq)
c       write(6,'(i2,1x,a7,1x,e14.8)') isec,'Bisec1',signb*aux1
c       write(6,'(i2,1x,a7,1x,e14.8)') isec,'Bisec2',signb*aux2
c       enddo
c          endif

       if(ibeam.eq.1) then
       write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.R1B1  := ',signb*a2(1),' + B11 * CMRSKEW + B12 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.L2B1  := ',signb*a2(1),' + B11 * CMRSKEW + B12 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.A23B1 := ',signb*a2(2),' + B21 * CMRSKEW + B22 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.R3B1  := ',signb*a2(3),' + B31 * CMRSKEW + B32 * CMISKEW',';'
          write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.L4B1  := ',signb*a2(3),' + B31 * CMRSKEW + B32 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.A45B1 := ',signb*a2(4),' + B41 * CMRSKEW + B42 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.R5B1  := ',signb*a2(5),' + B51 * CMRSKEW + B52 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.L6B1  := ',signb*a2(5),' + B51 * CMRSKEW + B52 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.A67B1 := ',signb*a2(6),' + B61 * CMRSKEW + B62 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.R7B1  := ',signb*a2(7),' + B71 * CMRSKEW + B72 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.L8B1  := ',signb*a2(7),' + B71 * CMRSKEW + B72 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.A81B1 := ',signb*a2(8),' + B81 * CMRSKEW + B82 * CMISKEW',';'
           elseif(ibeam.eq.2.or.ibeam.eq.4) then
       write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.A12B2 := ',signb*a2(1),' + B11 * CMRSKEW + B12 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.R2B2  := ',signb*a2(2),' + B21 * CMRSKEW + B22 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.L3B2  := ',signb*a2(2),' + B21 * CMRSKEW + B22 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.A34B2 := ',signb*a2(3),' + B31 * CMRSKEW + B32 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.R4B2  := ',signb*a2(4),' + B41 * CMRSKEW + B42 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.L5B2  := ',signb*a2(4),' + B41 * CMRSKEW + B42 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.A56B2 := ',signb*a2(5),' + B51 * CMRSKEW + B52 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.R6B2  := ',signb*a2(6),' + B61 * CMRSKEW + B62 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.L7B2  := ',signb*a2(6),' + B61 * CMRSKEW + B62 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.A78B2 := ',signb*a2(7),' + B71 * CMRSKEW + B72 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.R8B2  := ',signb*a2(8),' + B81 * CMRSKEW + B82 * CMISKEW',';'
           write(1,'(a16,e14.8,a32,1x,a1)')
     +'KQS.L1B2  := ',signb*a2(8),' + B81 * CMRSKEW + B82 * CMISKEW',';'
           endif
       write(1,*)

CPrintout b3 correction

       if(ibeam.eq.1) signb= 1.
       if(ibeam.eq.2) signb=-1.
       if(ibeam.eq.4) signb=-1.
       write(1,*) '!!! b3-correction for beam',ibeam
       if(ibeam.eq.1) then
       write(1,'(a16,e14.8,a12)')
     +    'KCS.a12B1  := ',signb*b3(1),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a23B1  := ',signb*b3(2),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a34B1  := ',signb*b3(3),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a45B1  := ',signb*b3(4),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a56B1  := ',signb*b3(5),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a67B1  := ',signb*b3(6),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a78B1  := ',signb*b3(7),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a81B1  := ',signb*b3(8),' /l.MCS ;'
           elseif(ibeam.eq.2.or.ibeam.eq.4) then
       write(1,'(a16,e14.8,a12)')
     +    'KCS.a12B2  := ',signb*b3(1),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a23B2  := ',signb*b3(2),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a34B2  := ',signb*b3(3),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a45B2  := ',signb*b3(4),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a56B2  := ',signb*b3(5),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a67B2  := ',signb*b3(6),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a78B2  := ',signb*b3(7),' /l.MCS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCS.a81B2  := ',signb*b3(8),' /l.MCS ;'
           endif
       write(1,*)

CPrintout a3 correction

       if(ibeam.eq.1) signb= 1.
       if(ibeam.eq.2) signb=-1.
       if(ibeam.eq.4) signb= 1.
       write(1,*) '!!! a3-correction for beam',ibeam
       if(ibeam.eq.1) then
       write(1,'(a16,e14.8,a12)')
     +    'KSS.a12B1  := ',signb*a3(1),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a23B1  := ',signb*a3(2),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a34B1  := ',signb*a3(3),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a45B1  := ',signb*a3(4),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a56B1  := ',signb*a3(5),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a67B1  := ',signb*a3(6),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a78B1  := ',signb*a3(7),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a81B1  := ',signb*a3(8),' /l.MSS ;'
           elseif(ibeam.eq.2.or.ibeam.eq.4) then
       write(1,'(a16,e14.8,a12)')
     +    'KSS.a12B2  := ',signb*a3(1),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a23B2  := ',signb*a3(2),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a34B2  := ',signb*a3(3),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a45B2  := ',signb*a3(4),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a56B2  := ',signb*a3(5),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a67B2  := ',signb*a3(6),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a78B2  := ',signb*a3(7),' /l.MSS ;'
           write(1,'(a16,e14.8,a12)')
     +    'KSS.a81B2  := ',signb*a3(8),' /l.MSS ;'
           endif
       write(1,*)
       write(1,*)

CPrintout b4 correction

       if(ibeam.eq.1) signb= 1.
       if(ibeam.eq.2) signb=-1.
       if(ibeam.eq.4) signb= 1.
       write(1,*) '!!! b4-correction for beam',ibeam
       if(ibeam.eq.1) then
       write(1,'(a16,e14.8,a12)')
     +    'KCO.a12B1  := ',signb*b4(1),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a23B1  := ',signb*b4(2),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a34B1  := ',signb*b4(3),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a45B1  := ',signb*b4(4),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a56B1  := ',signb*b4(5),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a67B1  := ',signb*b4(6),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a78B1  := ',signb*b4(7),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a81B1  := ',signb*b4(8),' /l.MCO ;'
           elseif(ibeam.eq.2.or.ibeam.eq.4) then
       write(1,'(a16,e14.8,a12)')
     +    'KCO.a12B2  := ',signb*b4(1),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a23B2  := ',signb*b4(2),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a34B2  := ',signb*b4(3),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a45B2  := ',signb*b4(4),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a56B2  := ',signb*b4(5),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a67B2  := ',signb*b4(6),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a78B2  := ',signb*b4(7),' /l.MCO ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCO.a81B2  := ',signb*b4(8),' /l.MCO ;'
           endif
       write(1,*)

CPrintout b5 correction

       if(ibeam.eq.1) signb= 1.
       if(ibeam.eq.2) signb=-1.
       if(ibeam.eq.4) signb=-1.
       write(1,*) '!!! b5-correction for beam',ibeam
       if(ibeam.eq.1) then
       write(1,'(a16,e14.8,a12)')
     +    'KCD.a12B1  := ',signb*b5(1),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a23B1  := ',signb*b5(2),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a34B1  := ',signb*b5(3),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a45B1  := ',signb*b5(4),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a56B1  := ',signb*b5(5),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a67B1  := ',signb*b5(6),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a78B1  := ',signb*b5(7),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a81B1  := ',signb*b5(8),' /l.MCD ;'
           elseif(ibeam.eq.2.or.ibeam.eq.4) then
       write(1,'(a16,e14.8,a12)')
     +    'KCD.a12B2  := ',signb*b5(1),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a23B2  := ',signb*b5(2),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a34B2  := ',signb*b5(3),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a45B2  := ',signb*b5(4),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a56B2  := ',signb*b5(5),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a67B2  := ',signb*b5(6),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a78B2  := ',signb*b5(7),' /l.MCD ;'
           write(1,'(a16,e14.8,a12)')
     +    'KCD.a81B2  := ',signb*b5(8),' /l.MCD ;'
           endif
       write(1,*)

       write(1,*) 'Return;'

       do i=1,2
       write(6,*) 'a2res', i, a2res(i)
       write(6,*) 'a3res', i, a3res(i)
       enddo

       stop
       end

       subroutine MINN(A,Nc,B)

       implicit none
       integer Nc,i,j,k,IFAIL
       real*8 A(Nc,8),B(8,Nc)
       real*8 At(8,Nc),Aaux(Nc,Nc)

       do i=1,8
       do j=1,Nc
       At(i,j)=A(j,i)
       B(i,j)=0.
       enddo
       enddo

       do i=1,Nc
       do j=1,Nc
       Aaux(i,j)=0.
       do k=1,8
       Aaux(i,j)=Aaux(i,j)+A(i,k)*At(k,j)
       enddo
       enddo
       enddo

       call DSINV(Nc,Aaux,Nc,IFAIL)
c       write(6,*) 'IFAIL=',IFAIL

       do i=1,8
       do j=1,Nc
       do k=1,Nc
       B(i,j)=B(i,j)-At(i,k)*Aaux(k,j)
       enddo
       enddo
       enddo

       return
       end


