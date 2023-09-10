css = """
<style>
section[data-testid="stSidebar"] button[kind=secondary]:first-of-type {
    background-color: #0099ff;
    color:#ffffff;
    width: 100%;
}
section[data-testid="stSidebar"] button[kind=secondary]:first-of-type:hover {
    background-color: #24a0ed;
    border-color: #24a0ed
}

section[data-testid="stSidebar"] [data-testid=stImage]{
    display: flex;
    margin-left: auto;
    margin-right: auto;
}

div[data-testid="column"]  h3 {
    height: 30px;
}
.main div[data-testid="stHorizontalBlock"]:nth-child(3) button[kind=secondary]:first-of-type {
    background-color: #4CAF50;
    color:#ffffff;
    margin-top: 34px;
    height: 100%;
}
</style>
"""
