*!version 1.0 2022-03-18
*open anything in Stata
cap program drop sopen
program define sopen 
version 16
if "`c(os)'"=="Windows" | "$S_MACH"=="PC"{
	sopenw `0'
}
else{
	sopenu `0'
}

end

cap program drop sopenu
program define sopenu

version 16

local isempty: word count `0'
if `isempty'==0{
	!open .
	 di `"{browse `"`c(pwd)'"'}"'
	 exit
}

syntax [anything] 

cap removequotes, t(`anything')
if _rc==0 {
	local anything `r(s)'
}
else{
	local anything `=usubinstr(`"`anything'"',"\","/",.)'
	!open `anything'
	exit
} 
local anything `=usubinstr(`"`anything'"',"\","/",.)'
local isurl1= ustrpos(`"`anything'"',"http://")
local isurl2=ustrpos(`"`anything'"',"https://")

if (`isurl1'>0 & `isurl1'<=2) |  (`isurl2'>0 & `isurl2'<=2){ //是url，直接打开
	!open `anything'
	exit
}

mata: st_numscalar("r(found)",direxists(`"`anything'"'))
local found = r(found)

if `found' ==0{
	mata: pathsplit(`"`anything'"',path1="",file2="")
	mata: st_local("path1",path1)
	mata: st_local("file2",file2)
	cap findfile `"`file2'"',path(`"`path1'"')
	if _rc==0 {
	   local found=1
	   local anything `r(fn)'
	}
}

local anything0 `anything'
local n: word count `anything'
if `n'>1{
	local anything `""`anything'""'
}	

if `found' { //路径存在直接打开
	!open `anything'
}
else{ //路径存在，可能存在特殊字符，尝试直接打开
	//cap findfile `anything'
	//if _rc==0{
	//    local anything `"`r(fn)'"'
	//	!open `anything'
    //}
	//if `"`path1'"'!=""{
	//	!open `anything'
	//}
	if regexm(`"`anything0'"',"^.*(\.app)$"){ //是app，尝试在Applications找该app
		local anything /Applications/`anything0'
		local n: word count `anything'
		if `n'>1{
			local anything `""`anything'""'
		}
		!open `anything'
		
	}
	else{
		!open `anything'
	}

}

end

cap program drop sopenw
program define sopenw

	version 16 
	local isempty: word count `0'
	if `isempty'==0{
	   cap winexec cmd /c start .
	   di `"{browse `"`c(pwd)'"'}"'
	   exit
	}

	syntax [anything]

	cap removequotes, t(`anything')
	if _rc==0{
		local anything `r(s)'
		} 
	else{
        local anything `=usubinstr(`"`anything'"',"/","\",.)'
	    //di `"`anything'"'		
		shellout `anything'
		exit
	} 
	

	local isurl1= ustrpos(`"`anything'"',"http://")
	local isurl2=ustrpos(`"`anything'"',"https://")

	if (`isurl1'>0 & `isurl1'<=2) |  (`isurl2'>0 & `isurl2'<=2){ //是url，直接打开
		!start `anything'
		exit
	}
    local anything `=usubinstr(`"`anything'"',"/","\",.)'
	local n: word count `anything'

	if `n'>1{
		local anything `""`anything'""'
	}


	cap findfile `anything'
	if _rc==0 {
		local anything `r(fn)'
	    local n: word count `anything'

		if `n'>1{
			local anything `""`anything'""'
		}


		shellout `anything'
	}
	else{
		shellout `anything'
	}	
end 

cap program drop shellout
program define shellout
version 16
syntax [anything]

cap winexec `anything'

 if _rc == 5| _rc==601 {
     !explorer `anything'
 }
 if _rc==193 {
   winexec cmd /c start ""  `anything'
 }
 if _rc==601 {
    noi di in yel `"`anything' not found."'
 }

end

//alternatively, using st_local 
cap program drop removequotes
program define removequotes,rclass
	version 16
	syntax, t(string)
	return local s `t'
end
