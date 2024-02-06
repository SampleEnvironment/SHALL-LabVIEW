<?xml version='1.0' encoding='UTF-8'?>
<Project Type="Project" LVVersion="23008000">
	<Property Name="SMProvider.SMVersion" Type="Int">201310</Property>
	<Item Name="My Computer" Type="My Computer">
		<Property Name="IOScan.Faults" Type="Str"></Property>
		<Property Name="IOScan.NetVarPeriod" Type="UInt">100</Property>
		<Property Name="IOScan.NetWatchdogEnabled" Type="Bool">false</Property>
		<Property Name="IOScan.Period" Type="UInt">10000</Property>
		<Property Name="IOScan.PowerupMode" Type="UInt">0</Property>
		<Property Name="IOScan.Priority" Type="UInt">9</Property>
		<Property Name="IOScan.ReportModeConflict" Type="Bool">true</Property>
		<Property Name="IOScan.StartEngineOnDeploy" Type="Bool">false</Property>
		<Property Name="NI.SortType" Type="Int">3</Property>
		<Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.tcp.enabled" Type="Bool">false</Property>
		<Property Name="server.tcp.port" Type="Int">0</Property>
		<Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
		<Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="random-demo" Type="Folder">
			<Item Name="dcy03.vi" Type="VI" URL="../dcy03.vi"/>
			<Item Name="dcy04.vi" Type="VI" URL="../dcy04.vi"/>
			<Item Name="dcy05.vi" Type="VI" URL="../dcy05.vi"/>
			<Item Name="dcy05_multimodule.vi" Type="VI" URL="../dcy05_multimodule.vi"/>
			<Item Name="dcy06.vi" Type="VI" URL="../dcy06.vi"/>
		</Item>
		<Item Name="SECoP.lvlib" Type="Library" URL="../SECoP.lvlib"/>
		<Item Name="LakeShore350empty.vi" Type="VI" URL="../LakeShore350empty.vi"/>
		<Item Name="LakeShore350.vi" Type="VI" URL="../LakeShore350.vi"/>
		<Item Name="LakeShore350Full.vi" Type="VI" URL="../LakeShore350Full.vi"/>
		<Item Name="Lake Shore 350.lvlib" Type="Library" URL="../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Lake Shore 350.lvlib"/>
		<Item Name="parametertype.ctl" Type="VI" URL="../parametertype.ctl"/>
		<Item Name="Dependencies" Type="Dependencies">
			<Item Name="vi.lib" Type="Folder">
				<Item Name="Clear Errors.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Clear Errors.vi"/>
				<Item Name="Error Cluster From Error Code.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Error Cluster From Error Code.vi"/>
				<Item Name="subTimeDelay.vi" Type="VI" URL="/&lt;vilib&gt;/express/express execution control/TimeDelayBlock.llb/subTimeDelay.vi"/>
			</Item>
			<Item Name="Initialize.vi" Type="VI" URL="/../../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Public/Initialize.vi"/>
			<Item Name="Close.vi" Type="VI" URL="/../../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Public/Close.vi"/>
			<Item Name="Sensor Data.vi" Type="VI" URL="/../../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Public/Data/Sensor Data.vi"/>
			<Item Name="Sensor Data (Single Reading).vi" Type="VI" URL="/../../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Public/Data/Sensor Data (Single Reading).vi"/>
			<Item Name="Setpoint Status.vi" Type="VI" URL="/../../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Public/Action-Status/Setpoint Status.vi"/>
			<Item Name="PID Status.vi" Type="VI" URL="/../../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Public/Action-Status/PID Status.vi"/>
			<Item Name="Configure PID.vi" Type="VI" URL="/../../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Public/Configure/Configure PID.vi"/>
			<Item Name="Configure Setpoint and Ramp.vi" Type="VI" URL="/../../Program Files (x86)/National Instruments/LabVIEW 2016/instr.lib/Lake Shore 350/Public/Configure/Configure Setpoint and Ramp.vi"/>
		</Item>
		<Item Name="Build Specifications" Type="Build">
			<Item Name="SECoP" Type="Source Distribution">
				<Property Name="Bld_autoIncrement" Type="Bool">true</Property>
				<Property Name="Bld_buildCacheID" Type="Str">{6572FBA0-730A-4685-8DAE-F061F6046784}</Property>
				<Property Name="Bld_buildSpecName" Type="Str">SECoP</Property>
				<Property Name="Bld_excludedDirectory[0]" Type="Path">vi.lib</Property>
				<Property Name="Bld_excludedDirectory[0].pathType" Type="Str">relativeToAppDir</Property>
				<Property Name="Bld_excludedDirectory[1]" Type="Path">resource/objmgr</Property>
				<Property Name="Bld_excludedDirectory[1].pathType" Type="Str">relativeToAppDir</Property>
				<Property Name="Bld_excludedDirectory[2]" Type="Path">/C/ProgramData/National Instruments/InstCache/16.0</Property>
				<Property Name="Bld_excludedDirectory[3]" Type="Path">/d/Profile/mjo/Eigene Dateien/LabVIEW Data/2016(64-bit)/ExtraVILib</Property>
				<Property Name="Bld_excludedDirectory[4]" Type="Path">instr.lib</Property>
				<Property Name="Bld_excludedDirectory[4].pathType" Type="Str">relativeToAppDir</Property>
				<Property Name="Bld_excludedDirectory[5]" Type="Path">user.lib</Property>
				<Property Name="Bld_excludedDirectory[5].pathType" Type="Str">relativeToAppDir</Property>
				<Property Name="Bld_excludedDirectoryCount" Type="Int">6</Property>
				<Property Name="Bld_localDestDir" Type="Path">../LLB/NI_AB_PROJECTNAME.llb</Property>
				<Property Name="Bld_localDestDirType" Type="Str">relativeToProject</Property>
				<Property Name="Bld_previewCacheID" Type="Str">{34AC44A7-62D0-4D88-A7BE-4FDC2C0BBBF8}</Property>
				<Property Name="Bld_version.build" Type="Int">2</Property>
				<Property Name="Bld_version.major" Type="Int">1</Property>
				<Property Name="Destination[0].destName" Type="Str">Destination Directory</Property>
				<Property Name="Destination[0].path" Type="Path">../LLB/NI_AB_PROJECTNAME.llb</Property>
				<Property Name="Destination[0].path.type" Type="Str">relativeToProject</Property>
				<Property Name="Destination[0].type" Type="Str">LLB</Property>
				<Property Name="Destination[1].destName" Type="Str">Support Directory</Property>
				<Property Name="Destination[1].path" Type="Path">../data</Property>
				<Property Name="Destination[1].path.type" Type="Str">relativeToProject</Property>
				<Property Name="DestinationCount" Type="Int">2</Property>
				<Property Name="Source[0].itemID" Type="Str">{E5411664-9AC7-4BC8-9F41-6C54A109AC55}</Property>
				<Property Name="Source[0].type" Type="Str">Container</Property>
				<Property Name="Source[1].destinationIndex" Type="Int">0</Property>
				<Property Name="Source[1].itemID" Type="Ref">/My Computer/SECoP.lvlib/Public/SECoP-simpleStringFromJSON.vi</Property>
				<Property Name="Source[1].sourceInclusion" Type="Str">Include</Property>
				<Property Name="Source[1].type" Type="Str">VI</Property>
				<Property Name="Source[2].destinationIndex" Type="Int">0</Property>
				<Property Name="Source[2].itemID" Type="Ref">/My Computer/SECoP.lvlib/Public/SECoP-simpleStringToJSON.vi</Property>
				<Property Name="Source[2].sourceInclusion" Type="Str">Include</Property>
				<Property Name="Source[2].type" Type="Str">VI</Property>
				<Property Name="Source[3].destinationIndex" Type="Int">0</Property>
				<Property Name="Source[3].itemID" Type="Ref">/My Computer/SECoP.lvlib/Public/SECoP-TimeStamp.vi</Property>
				<Property Name="Source[3].sourceInclusion" Type="Str">Include</Property>
				<Property Name="Source[3].type" Type="Str">VI</Property>
				<Property Name="SourceCount" Type="Int">4</Property>
			</Item>
		</Item>
	</Item>
</Project>
